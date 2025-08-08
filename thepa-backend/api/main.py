# api/main.py
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
from datetime import datetime
from io import BytesIO
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

# 🚀 สร้าง FastAPI app
app = FastAPI(title="THEPA Backend API", version="1.0.0")

# 🔥 CORS - เพิ่ม Frontend URL ที่ deploy แล้ว
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://rextambunx-github-io.vercel.app",  # Frontend URL ของคุณ
        "https://*.vercel.app",
        "http://10.7.0.111:3000/"
        "*"  # สำหรับ testing (production ควรระบุ specific domains)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 📁 File paths สำหรับ Vercel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # ขึ้นไป 1 level จาก api/

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "templates")
TEMP_DIR = "/tmp"  # Vercel temp directory

# สร้างโฟลเดอร์ถ้าไม่มี
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# File paths
DATA_FILE = os.path.join(DATA_DIR, "lease_questions.json")
ANSWERS_FILE = os.path.join(DATA_DIR, "saved_answers.json")
GROUP_SECTION_FILE = os.path.join(DATA_DIR, "group_section.json")
TEMPLATE_FILE = os.path.join(TEMPLATE_DIR, "contract_template.docx")

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
    return {"title": "Legal Document Generator", "nodes": []}

def save_questions(data):
    """บันทึกคำถามลงไฟล์ JSON"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_answer_by_id(answer_id):
    """โหลดคำตอบตาม ID"""
    if not os.path.exists(ANSWERS_FILE):
        return {}
    with open(ANSWERS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    if answer_id >= len(data):
        return {}
    return flatten_answer([data[answer_id]])

def flatten_answer(answer_list):
    """รวมคำตอบทั้งหมดเข้าเป็น dict เดียว"""
    combined = {}
    for ans in answer_list:
        if isinstance(ans, dict):
            for key, inner_dict in ans.items():
                if isinstance(inner_dict, dict):
                    combined.update(inner_dict)
                else:
                    combined[key] = inner_dict
    return combined

# ======= API ENDPOINTS =======

# 🏥 Health Check
@app.get("/")
def root():
    return {
        "message": "THEPA Backend API is running! 🚀", 
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": ["/questions", "/save_answers", "/generate", "/health"]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "data_files_exist": {
            "questions": os.path.exists(DATA_FILE),
            "answers": os.path.exists(ANSWERS_FILE),
            "groups": os.path.exists(GROUP_SECTION_FILE)
        }
    }

# 📋 Questions API
@app.get("/questions")
def get_questions():
    """GET คำถามทั้งหมด"""
    try:
        return load_questions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading questions: {str(e)}")

@app.post("/questions")
async def update_questions(request: Request):
    """POST อัปเดตคำถาม"""
    try:
        data = await request.json()
        save_questions(data)
        return {"message": "Questions updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating questions: {str(e)}")

@app.get("/api/lease_questions")
def get_lease_questions():
    """GET รายการคำถาม (เฉพาะ id กับ question)"""
    try:
        data = load_questions()
        nodes = data.get("nodes", [])
        questions = [{"id": node["id"], "question": node["question"]} for node in nodes]
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading lease questions: {str(e)}")

# 💾 Answers API
@app.post("/save_answers")
async def save_answers(request: Request):
    """POST บันทึกคำตอบ"""
    try:
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

        # คำนวณหมายเลข Answer
        answer_number = len(all_data) + 1
        wrapped_data = {f"Answer {answer_number}": new_data}
        all_data.append(wrapped_data)

        # เขียนกลับไปยังไฟล์
        with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        return {"message": f"Saved as Answer {answer_number}", "answer_id": answer_number}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving answers: {str(e)}")

@app.get("/get_all_answers")
def get_all_answers():
    """GET คำตอบทั้งหมด (merged format)"""
    try:
        if not os.path.exists(ANSWERS_FILE):
            return {}
        
        with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged = {}
            for entry in data:
                if isinstance(entry, dict):
                    merged.update(entry)
            return merged
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading answers: {str(e)}")

@app.get("/answers/all")
def get_all_answers_raw():
    """GET คำตอบทั้งหมด (raw format)"""
    try:
        if not os.path.exists(ANSWERS_FILE):
            return []
        with open(ANSWERS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading raw answers: {str(e)}")

@app.get("/answers")
def get_answers(index: int = 0):
    """GET คำตอบตาม index"""
    try:
        if not os.path.exists(ANSWERS_FILE):
            return {"error": "No answers found"}
        
        with open(ANSWERS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if index < 0 or index >= len(data):
            return {"error": "Invalid index"}
        return flatten_answer([data[index]])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading answer by index: {str(e)}")

# 📄 Document Generation API
@app.post("/preview")
def preview(req: DocRequest):
    """POST ดูตัวอย่างเอกสาร"""
    try:
        data = req.data or load_answer_by_id(req.answer_id)
        rendered = Template(req.template).render(data)
        return {"rendered": rendered.replace("\n", "<br>")}
    except Exception as e:
        return {"error": f"Template error: {str(e)}"}

@app.post("/generate")
def generate_doc(req: DocRequest):
    """POST สร้างเอกสาร Word"""
    try:
        data = req.data or load_answer_by_id(req.answer_id)
        rendered = Template(req.template).render(data)
        
        doc = Document()
        for line in rendered.split('\n'):
            if line.strip():
                doc.add_paragraph(line)
        
        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=document.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

@app.post("/generate_pdf")
def generate_pdf(req: DocRequest):
    """POST สร้างเอกสาร PDF"""
    try:
        data = req.data or load_answer_by_id(req.answer_id)
        rendered = Template(req.template).render(data)
        
        # แปลง **text** เป็น <b>text</b>
        converted_text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", rendered)
        
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        
        story = []
        for line in converted_text.split("\n"):
            line = line.strip()
            if line:
                story.append(Paragraph(line, normal_style))
        
        doc.build(story)
        buf.seek(0)
        
        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=document.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

# 📂 Group Management API
@app.post("/api/section_groups")
async def save_section_group(group: SectionGroup):
    """POST บันทึกกลุ่มคำถาม"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving section group: {str(e)}")

@app.get("/api/group-section")
def get_group_section():
    """GET ข้อมูลกลุ่มคำถาม"""
    try:
        if not os.path.exists(GROUP_SECTION_FILE):
            return []
        with open(GROUP_SECTION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading group sections: {str(e)}")

# 🔥 สำคัญ: Export app สำหรับ Vercel
# Vercel จะใช้ตัวนี้เป็น entry point