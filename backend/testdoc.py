from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jinja2 import Template
from docx import Document
from fastapi.responses import StreamingResponse
from typing import List
import os
from io import BytesIO
import json
from fastapi import Query
from fastapi import Body
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import re


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROUP_SECTION_FILE = "data/group_section.json"
TEMPLATE_FOLDER = "templates"

class DocRequest(BaseModel):
    template: str
    data: dict = {}  # Optional: รองรับแบบส่งตรง
    answer_id: int = 0

class TemplateSaveRequest(BaseModel):
    name: str
    content: str

class SectionGroup(BaseModel):
    groupName: str
    questionIds: List[str]

def save_section_group(payload):
    filename = GROUP_SECTION_FILE

    # ถ้าไฟล์ไม่มีหรือว่าง ให้เริ่มจาก list ว่าง
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        data = []
    else:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

    # เพิ่ม group ใหม่เข้าไป
    data.append(payload)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {"status": "ok"}

def load_answer_by_id(answer_id):
    with open("data/saved_answers.json", encoding="utf-8") as f:
        data = json.load(f)
    if answer_id >= len(data):
        return {}
    return flatten_answer([data[answer_id]])

def flatten_answer(answer_list):
    combined = {}
    for ans in answer_list:
        for key, inner_dict in ans.items():
            combined.update(inner_dict)
    return combined

@app.get("/answers/all")
def get_all_answers():
    with open("data/saved_answers.json", encoding="utf-8") as f:
        return json.load(f)

@app.get("/answers")
def get_answers(index: int = 0):
    with open("data/saved_answers.json", encoding="utf-8") as f:
        data = json.load(f)
    if index < 0 or index >= len(data):
        return {"error": "Invalid index"}
    flat_data = flatten_answer([data[index]])
    return flat_data


@app.get("/templates", response_model=List[str])
def get_template_list():
    return [f.replace(".txt", "") for f in os.listdir(TEMPLATE_FOLDER) if f.endswith(".txt")]

@app.get("/template/{name}")
def get_template(name: str):
    path = os.path.join(TEMPLATE_FOLDER, f"{name}.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return {"name": name, "content": f.read()}
    return {"error": "not found"}

@app.post("/template/save")
def save_template(req: TemplateSaveRequest):
    path = os.path.join(TEMPLATE_FOLDER, f"{req.name}.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(req.content)
        return {"status": "success", "message": f"Template '{req.name}' saved."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/preview")
def preview(req: DocRequest):
    data = req.data or load_answer_by_id(req.answer_id)
    rendered = Template(req.template).render(data)
    return {"rendered": rendered.replace("\n", "<br>")}

@app.post("/generate")
def generate_doc(req: DocRequest):
    data = req.data or load_answer_by_id(req.answer_id)
    rendered = Template(req.template).render(data)
    doc = Document()
    for line in rendered.split('\n'):
        doc.add_paragraph(line)
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
        "Content-Disposition": "attachment; filename=generated.docx"
    })

@app.post("/generate_pdf")
def generate_pdf(req: DocRequest):
    data = req.data or load_answer_by_id(req.answer_id)
    rendered = Template(req.template).render(data)

    # แปลง **text** เป็น <b>text</b> เพื่อใช้กับ reportlab paragraph
    def convert_bold(text):
        # แปลง **text** เป็น <b>text</b>
        return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

    converted_text = convert_bold(rendered)

    # สร้าง PDF ลงใน BytesIO buffer
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.fontName = 'Helvetica'
    normal_style.fontSize = 12
    normal_style.leading = 16

    # แยกบรรทัดแล้วสร้าง Paragraph ทีละบรรทัด (Paragraph รองรับ HTML tags พื้นฐาน <b>)
    story = []
    for line in converted_text.split("\n"):
        line = line.strip()
        if line:
            story.append(Paragraph(line, normal_style))
        story.append(Paragraph("<br/>", normal_style))  # เว้นวรรคบรรทัด

    doc.build(story)

    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=generated.pdf"
        }
    )

@app.post("/api/section_groups")
async def save_section_group(group: SectionGroup):
    if os.path.exists(GROUP_SECTION_FILE) and os.path.getsize(GROUP_SECTION_FILE) > 0:
        with open(GROUP_SECTION_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(group.dict())

    with open(GROUP_SECTION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {"message": "บันทึกกลุ่มคำถามเรียบร้อยแล้ว", "group": group}


@app.get("/api/lease_questions")
def get_lease_questions():
    with open("data/lease_questions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = data.get("nodes", [])
    # สร้าง list ใหม่เฉพาะ id กับ question
    questions = [{"id": node["id"], "question": node["question"]} for node in nodes]
    return questions



import uvicorn

if __name__ == "__main__":
    uvicorn.run("testdoc:app", host="0.0.0.0", port=8002, reload=True)
