from flask import Flask, request, jsonify
import joblib
import numpy as np

# โหลดโมเดลที่ฝึกไว้
model = joblib.load("earthquake_modelss2.pkl")

# สร้าง Flask app
app = Flask(__name__)

# Endpoint สำหรับทำนายการสั่น
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # รับข้อมูลจาก client (ค่าจากเซ็นเซอร์)
        data = request.get_json()

        # ดึงค่า ax, ay, az, gx, gy, gz
        ax = data['ax']
        ay = data['ay']
        az = data['az']
        gx = data['gx']
        gy = data['gy']
        gz = data['gz']

        # เตรียมข้อมูลสำหรับทำนาย
        sample = np.array([[ax, ay, az, gx, gy, gz]])

        # ทำนายผลลัพธ์
        prediction = model.predict(sample)[0]

        # รายชื่อ label
        labels = {
            0: "ไม่มีการสั่น",
            1: "สั่นเบา",
            2: "สั่นปานกลาง",
            3: "สั่นรุนแรง",
            4: "สั่นรุนแรงมาก"
        }

        # คำนวณความมั่นใจ (เฉพาะถ้าโมเดลรองรับ)
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(sample)[0]
            confidence = round(np.max(proba) * 100, 2)  # เปอร์เซ็นต์ความมั่นใจ
        else:
            confidence = None

        # ส่งผลลัพธ์กลับไปให้ client
        return jsonify({
            'prediction': labels[prediction],
            'confidence_percent': confidence
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# รัน Flask server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
