from fastapi import FastAPI, Request, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from jinja2 import Template
from docx import Document
from docxtpl import DocxTemplate
from typing import List
import json
import os
import uvicorn
from datetime import datetime
from io import BytesIO
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ควรระบุ origin จริงใน production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======= FILE PATHS =======
TEMPLATE_FILE = "templates/contract_template.docx"
DATA_FILE = "data/lease_questions.json"
ANSWERS_FILE = "data/saved_answers.json"
GROUP_SECTION_FILE = "data/group_section.json"
TEMPLATE_FOLDER = "templates"

# ======= PYDANTIC MODELS =======
class Group(BaseModel):
    groupName: str
    questionIds: List[str]

class AddQuestionRequest(BaseModel):
    groupName: str
    questionId: str

class AddQuestionsRequest(BaseModel):
    groupName: str
    newQuestionIds: List[str]

class DocRequest(BaseModel):
    template: str
    data: dict = {}
    answer_id: int = 0

class TemplateSaveRequest(BaseModel):
    name: str
    content: str

class SectionGroup(BaseModel):
    groupName: str
    questionIds: List[str]

# ======= UTILITY FUNCTIONS =======
def load_questions():
    """โหลดคำถามจากไฟล์ JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"title": "", "nodes": []}

def save_questions(data):
    """บันทึกคำถามลงไฟล์ JSON"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_questions_to_file(data):
    """บันทึกคำถามลงไฟล์ JSON (alias function)"""
    save_questions(data)

def reorder_question_ids(data):
    """จัดเรียง ID คำถามใหม่เป็น q1, q2, q3..."""
    old_to_new = {}
    new_nodes = []

    # จัดเรียงใหม่เป็น q1, q2, ...
    for i, node in enumerate(data["nodes"]):
        new_id = f"q{i+1}"
        old_to_new[node["id"]] = new_id

    # อัปเดต node
    for i, node in enumerate(data["nodes"]):
        updated_node = node.copy()
        updated_node["id"] = old_to_new[node["id"]]
        
        # อัปเดต next ถ้ามี
        if "next" in updated_node and updated_node["next"] in old_to_new:
            updated_node["next"] = old_to_new[updated_node["next"]]

        # อัปเดต options[].next ถ้ามี
        if updated_node.get("type") == "dropdown":
            for opt in updated_node.get("options", []):
                if opt.get("next") in old_to_new:
                    opt["next"] = old_to_new[opt["next"]]

        new_nodes.append(updated_node)

    return {
        "title": data.get("title", ""),
        "nodes": new_nodes
    }

def load_answer_by_id(answer_id):
    """โหลดคำตอบตาม ID"""
    with open(ANSWERS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    if answer_id >= len(data):
        return {}
    return flatten_answer([data[answer_id]])

def flatten_answer(answer_list):
    """รวมคำตอบทั้งหมดเข้าเป็น dict เดียว"""
    combined = {}
    for ans in answer_list:
        for key, inner_dict in ans.items():
            combined.update(inner_dict)
    return combined

def load_groups() -> List[Group]:
    """โหลดข้อมูลกลุ่มคำถาม"""
    if not os.path.exists(GROUP_SECTION_FILE):
        return []
    with open(GROUP_SECTION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Group(**g) for g in data]

def save_groups(groups: List[Group]):
    """บันทึกข้อมูลกลุ่มคำถาม"""
    with open(GROUP_SECTION_FILE, "w", encoding="utf-8") as f:
        json.dump([g.dict() for g in groups], f, ensure_ascii=False, indent=2)

def render_contract_from_answer(answer_key: str, output_file="contract_output.docx"):
    """สร้างสัญญาจาก Answer key โดยใช้ DocxTemplate"""
    with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    # ค้นหา answer_key ใน list
    answers = None
    for entry in all_data:
        if isinstance(entry, dict) and answer_key in entry:
            answers = entry[answer_key]
            break

    if not answers:
        raise ValueError(f"ไม่พบคำตอบใน Answer key: {answer_key}")

    # สร้าง context สำหรับใส่ใน template
    context = {
        "place": answers.get("q2: ข้อตกลงจะลงนามที่ไหน?", ""),
        "sign_date": answers.get("q3: ข้อตกลงจะลงนามในวันไหน?", ""),
        "shareholder1": answers.get("q4: ตามกฎหมายบริษัทไทย บริษัทจำกัดจำเป็นต้องมีผู้ถือหุ้นอย่างน้อยหนึ่งคน ผู้ถือหุ้นคนแรกชื่ออะไร?", ""),
        "shareholder2": answers.get("q14: ผู้ถือหุ้นคนที่สองชื่ออะไร?", ""),
        "shareholder3": answers.get("q15: ผู้ถือหุ้นคนที่สามชื่ออะไร?", ""),
        "effective_date": answers.get("q12: ข้อตกลงนี้จะมีผลบังคับใช้ในวันไหน?", ""),
        "lawyer_info": answers.get("q25: ข้อมูลของทนาย [ชื่อ, นามสกุล, เลขทะเบียน] ", "")
    }

    # โหลดและใส่ข้อมูลใน docx template
    doc = DocxTemplate(TEMPLATE_FILE)
    doc.render(context)
    doc.save(output_file)

    print(f"✅ เอกสารถูกสร้างแล้ว: {output_file}")

# ======= API ENDPOINTS - QUESTIONS =======
@app.get("/questions")
def get_questions():
    """GET คำถามทั้งหมด"""
    return load_questions()

@app.post("/questions")
async def update_questions(request: Request):
    """POST อัปเดตคำถาม"""
    data = await request.json()
    save_questions_to_file(data)
    return {"message": "Updated successfully"}

@app.get("/api/lease_questions")
def get_lease_questions():
    """GET รายการคำถาม (เฉพาะ id กับ question)"""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = data.get("nodes", [])
    questions = [{"id": node["id"], "question": node["question"]} for node in nodes]
    return questions

# ======= API ENDPOINTS - ANSWERS =======
@app.post("/save_answers")
async def save_answers(request: Request):
    """POST บันทึกคำตอบ"""
    new_data = await request.json()

    # โหลดข้อมูลเก่า
    if os.path.exists(ANSWERS_FILE):
        with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
            try:
                all_data = json.load(f)
                if not isinstance(all_data, list):
                    all_data = [all_data]
            except json.JSONDecodeError:
                all_data = []
    else:
        all_data = []

    # คำนวณหมายเลข Answer (นับจาก 1)
    answer_number = len(all_data) + 1
    wrapped_data = {
        f"Answer {answer_number}": new_data
    }

    # เพิ่มข้อมูลใหม่
    all_data.append(wrapped_data)

    # เขียนกลับไปยังไฟล์
    os.makedirs(os.path.dirname(ANSWERS_FILE), exist_ok=True)
    with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    return {"message": f"Saved as Answer {answer_number}"}

@app.get("/get_all_answers")
def get_all_answers():
    """GET คำตอบทั้งหมด (รูปแบบ merged)"""
    if os.path.exists(ANSWERS_FILE):
        with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # แปลงจาก list ของ dict เป็น dict เดียว
                merged = {}
                for entry in data:
                    if isinstance(entry, dict):
                        merged.update(entry)
                return merged
            except:
                return {}
    return {}

@app.get("/answers/all")
def get_all_answers_raw():
    """GET คำตอบทั้งหมด (รูปแบบ raw)"""
    with open(ANSWERS_FILE, encoding="utf-8") as f:
        return json.load(f)

@app.get("/answers")
def get_answers(index: int = 0):
    """GET คำตอบตาม index"""
    with open(ANSWERS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    if index < 0 or index >= len(data):
        return {"error": "Invalid index"}
    flat_data = flatten_answer([data[index]])
    return flat_data

# ======= API ENDPOINTS - DOCUMENT GENERATION =======
@app.post("/generate_docx")
async def generate_docx(request: Request):
    """สร้างไฟล์สัญญาเป็น .docx จาก Answer ID"""
    data = await request.json()
    answer_key = data.get("answer_key")
    if not answer_key:
        return {"error": "กรุณาระบุ answer_key"}

    try:
        output_dir = "generated_docs"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"สัญญา_{answer_key}.docx"
        filepath = os.path.join(output_dir, filename)

        render_contract_from_answer(answer_key, filepath)
        return {"message": "สร้างเอกสารสำเร็จ", "filename": filename}
    except Exception as e:
        return {"error": str(e)}

@app.get("/download_docx/{filename}")
def download_docx(filename: str):
    """ดาวน์โหลดไฟล์ .docx"""
    file_path = f"generated_docs/{filename}"
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    return {"error": "ไม่พบไฟล์"}

# ======= API ENDPOINTS - TEMPLATES =======
@app.get("/templates", response_model=List[str])
def get_template_list():
    """GET รายการ template ทั้งหมด"""
    return [f.replace(".txt", "") for f in os.listdir(TEMPLATE_FOLDER) if f.endswith(".txt")]

@app.get("/template/{name}")
def get_template(name: str):
    """GET template ตามชื่อ"""
    path = os.path.join(TEMPLATE_FOLDER, f"{name}.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return {"name": name, "content": f.read()}
    return {"error": "not found"}

@app.post("/template/save")
def save_template(req: TemplateSaveRequest):
    """POST บันทึก template"""
    path = os.path.join(TEMPLATE_FOLDER, f"{req.name}.txt")
    try:
        os.makedirs(TEMPLATE_FOLDER, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(req.content)
        return {"status": "success", "message": f"Template '{req.name}' saved."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/preview")
def preview(req: DocRequest):
    """POST ดูตัวอย่างเอกสาร"""
    data = req.data or load_answer_by_id(req.answer_id)
    rendered = Template(req.template).render(data)
    return {"rendered": rendered.replace("\n", "<br>")}

@app.post("/generate")
def generate_doc(req: DocRequest):
    """POST สร้างเอกสาร Word"""
    data = req.data or load_answer_by_id(req.answer_id)
    rendered = Template(req.template).render(data)
    doc = Document()
    for line in rendered.split('\n'):
        doc.add_paragraph(line)
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, 
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=generated.docx"})

@app.post("/generate_pdf")
def generate_pdf(req: DocRequest):
    """POST สร้างเอกสาร PDF"""
    data = req.data or load_answer_by_id(req.answer_id)
    rendered = Template(req.template).render(data)

    # แปลง **text** เป็น <b>text</b> เพื่อใช้กับ reportlab paragraph
    def convert_bold(text):
        return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

    converted_text = convert_bold(rendered)

    # สร้าง PDF ลงใน BytesIO buffer
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, 
                           topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.fontName = 'Helvetica'
    normal_style.fontSize = 12
    normal_style.leading = 16

    # แยกบรรทัดแล้วสร้าง Paragraph ทีละบรรทัด
    story = []
    for line in converted_text.split("\n"):
        line = line.strip()
        if line:
            story.append(Paragraph(line, normal_style))
        story.append(Paragraph("<br/>", normal_style))

    doc.build(story)
    buf.seek(0)

    return StreamingResponse(buf, media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=generated.pdf"})

# ======= API ENDPOINTS - GROUP SECTIONS =======
@app.post("/api/section_groups")
async def save_section_group(group: SectionGroup):
    """POST บันทึกกลุ่มคำถาม"""
    if os.path.exists(GROUP_SECTION_FILE) and os.path.getsize(GROUP_SECTION_FILE) > 0:
        with open(GROUP_SECTION_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(group.dict())
    os.makedirs(os.path.dirname(GROUP_SECTION_FILE), exist_ok=True)

    with open(GROUP_SECTION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {"message": "บันทึกกลุ่มคำถามเรียบร้อยแล้ว", "group": group}

@app.get("/api/group-section")
def get_group_section():
    """GET ข้อมูลกลุ่มคำถาม"""
    if not os.path.exists(GROUP_SECTION_FILE):
        return []
    with open(GROUP_SECTION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@app.get("/api/section_g")
def get_section_groups():
    """GET ข้อมูลกลุ่มคำถาม (alias)"""
    if not os.path.exists(GROUP_SECTION_FILE):
        return []
    with open(GROUP_SECTION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/section_asd")
async def get_section_groups_asd():
    """GET ข้อมูลกลุ่มคำถาม (alias 2)"""
    if os.path.exists(GROUP_SECTION_FILE) and os.path.getsize(GROUP_SECTION_FILE) > 0:
        with open(GROUP_SECTION_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    return data

@app.delete("/api/group_section/{question_id}")
def remove_question_from_groups(question_id: str):
    """DELETE ลบคำถามออกจากกลุ่ม"""
    if not os.path.exists(GROUP_SECTION_FILE):
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์ group_section.json")

    with open(GROUP_SECTION_FILE, "r", encoding="utf-8") as f:
        try:
            groups = json.load(f)
        except json.JSONDecodeError:
            groups = []

    updated = False
    for group in groups:
        if "questionIds" in group and question_id in group["questionIds"]:
            group["questionIds"] = [qid for qid in group["questionIds"] if qid != question_id]
            updated = True

    if not updated:
        raise HTTPException(status_code=404, detail="ไม่พบ questionId ใน group_section.json")

    with open(GROUP_SECTION_FILE, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)

    return {"message": f"ลบคำถาม {question_id} จาก group_section.json เรียบร้อยแล้ว"}

@app.post("/api/section_groups/add_questions")
def add_questions(req: AddQuestionsRequest):
    """POST เพิ่มคำถามหลายข้อเข้ากลุ่ม"""
    if not os.path.exists(GROUP_SECTION_FILE):
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์ group_section.json")
    
    with open(GROUP_SECTION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    group_found = False
    for group in data:
        if group["groupName"] == req.groupName:
            existing = set(group["questionIds"])
            for qid in req.newQuestionIds:
                if qid not in existing:
                    group["questionIds"].append(qid)
            group_found = True
            break
    
    if not group_found:
        raise HTTPException(status_code=404, detail="ไม่พบกลุ่มที่ระบุ")

    with open(GROUP_SECTION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return {"message": "เพิ่มคำถามเรียบร้อยแล้ว"}

@app.get("/groups", response_model=List[Group])
def get_groups():
    """GET รายการกลุ่ม (Pydantic model)"""
    return load_groups()

@app.post("/groups/add-question")
def add_question_to_group(req: AddQuestionRequest):
    """POST เพิ่มคำถามเข้ากลุ่ม"""
    groups = load_groups()
    updated = False

    for group in groups:
        if group.groupName == req.groupName:
            if req.questionId not in group.questionIds:
                group.questionIds.append(req.questionId)
                updated = True

    if not updated:
        raise HTTPException(status_code=404, detail="ไม่พบกลุ่มหรือคำถามซ้ำ")

    save_groups(groups)
    return {"message": "เพิ่มคำถามสำเร็จ", "groupName": req.groupName, "questionId": req.questionId}

# ======= MAIN =======
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)