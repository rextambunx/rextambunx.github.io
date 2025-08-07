from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import uvicorn
from docxtpl import DocxTemplate
from datetime import datetime
from fastapi.responses import FileResponse

app = FastAPI()

# ให้ Frontend เข้าถึงได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ควรระบุ origin จริงใน production
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATE_FILE = "templates/contract_template.docx"

# Path ของไฟล์ JSON ที่เก็บคำถาม
DATA_FILE = "data/lease_questions.json"

# Path ของไฟล์คำตอบ
ANSWERS_FILE = "data/saved_answers.json"

# โหลดคำถามจากไฟล์ JSON
def load_questions():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"title": "", "nodes": []}

# บันทึกคำถามลงไฟล์ JSON
def save_questions(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def reorder_question_ids(data):
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

# บันทึกคำตอบลงไฟล์ JSON
def save_questions_to_file(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def render_contract_from_answer(answer_key: str, output_file="contract_output.docx"):
    with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    # 🔍 ค้นหา answer_key ใน list
    answers = None
    for entry in all_data:
        if isinstance(entry, dict) and answer_key in entry:
            answers = entry[answer_key]
            break

    if not answers:
        raise ValueError(f"ไม่พบคำตอบใน Answer key: {answer_key}")

    # 🔧 สร้าง context สำหรับใส่ใน template
    context = {
        "place": answers.get("q2: ข้อตกลงจะลงนามที่ไหน?", ""),
        "sign_date": answers.get("q3: ข้อตกลงจะลงนามในวันไหน?", ""),
        "shareholder1": answers.get("q4: ตามกฎหมายบริษัทไทย บริษัทจำกัดจำเป็นต้องมีผู้ถือหุ้นอย่างน้อยหนึ่งคน ผู้ถือหุ้นคนแรกชื่ออะไร?", ""),
        "shareholder2": answers.get("q14: ผู้ถือหุ้นคนที่สองชื่ออะไร?", ""),
        "shareholder3": answers.get("q15: ผู้ถือหุ้นคนที่สามชื่ออะไร?", ""),
        "effective_date": answers.get("q12: ข้อตกลงนี้จะมีผลบังคับใช้ในวันไหน?", ""),
        "lawyer_info": answers.get("q25: ข้อมูลของทนาย [ชื่อ, นามสกุล, เลขทะเบียน] ", "")
    }

    # 📝 โหลดและใส่ข้อมูลใน docx template
    doc = DocxTemplate(TEMPLATE_FILE)
    doc.render(context)
    doc.save(output_file)

    print(f"✅ เอกสารถูกสร้างแล้ว: {output_file}")




# API: GET คำถามทั้งหมด
@app.get("/questions")
def get_questions():
    return load_questions()

# API: POST อัปเดตคำถาม
@app.post("/questions")
async def update_questions(request: Request):
    data = await request.json()
    save_questions_to_file(data)
    return {"message": "Updated successfully"}

# POST บันทึกคำตอบ
@app.post("/save_answers")
async def save_answers(request: Request):
    new_data = await request.json()

    # ✅ โหลดข้อมูลเก่า
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

    # ✅ คำนวณหมายเลข Answer (นับจาก 1)
    answer_number = len(all_data) + 1
    wrapped_data = {
        f"Answer {answer_number}": new_data
    }

    # ✅ เพิ่มข้อมูลใหม่
    all_data.append(wrapped_data)

    # ✅ เขียนกลับไปยังไฟล์
    os.makedirs(os.path.dirname(ANSWERS_FILE), exist_ok=True)
    with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    return {"message": f"Saved as Answer {answer_number}"}

# สร้างไฟล์สัญญาเป็น .docx จาก Answer ID
@app.post("/generate_docx")
async def generate_docx(request: Request):
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


@app.get("/get_all_answers")
def get_all_answers():
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

@app.get("/download_docx/{filename}")
def download_docx(filename: str):
    file_path = f"generated_docs/{filename}"
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    return {"error": "ไม่พบไฟล์"}

# รันเซิร์ฟเวอร์
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
