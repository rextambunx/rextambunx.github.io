# โปรเจ็กต์ของ Project_BUU_ESE-AB-67-01

## 📌 วิธีการใช้งาน

### 1. ติดตั้ง Node-red และ Node.js
- ดาวน์โหลด Node.js (แนะนำเวอร์ชัน LTS) ได้จาก [https://nodejs.org](https://nodejs.org)
- ติดตั้งตามขั้นตอนปกติ
- ตรวจสอบว่า Node.js และ npm ติดตั้งสำเร็จแล้ว:
  ```bash
  node -v
  npm -v
### 2.ติดตั้ง Node-RED
- เปิด Command Prompt หรือ PowerShell แล้วรันคำสั่ง:
  ```bash
  npm install -g --unsafe-perm node-red
### 3.จากนั้นติดตั้ง Pagekage ส่วนเสริม ของ Node-red:
- เปิด Command Prompt หรือ PowerShell แล้วรันคำสั่ง:
  ```bash
  npm install @flowfuse/node-red-dashboard-2-ui-flowviewer @flowfuse/node-red-dashboard-2-ui-iframe @flowfuse/node-red-dashboard-2-ui-led @flowfuse/node-red-dashboard
### 4.จากนั้นโหลดในส่วนของ Model Python.pkl, noderedProject.json และ serverprediction:
- ลิ้งโหลดใน Github
  ```bash
    https://github.com/rextambunx/rextambunx.github.io/tree/master/Project_BUU_ESE-AB-67-01
### 5. ทำการเปิด Server ใน RaspberryPi4
- เปิด Terminal แล้วใช้คำสั่งนี้
  ```bash
  sudo apt install -y python3-venv
  python3 -m venv myenv
  source myenv/bin/activate
- ทำการเข้าไฟล์ python โดยการเข้าไปที่ที่เก็บโฟลเดอร์นั้น ในตัวอย่างใช้ชื่อไฟล์ sl.py จากนั้นใช้คำสั่ง
  ```bash
  python sl.py
- เมื่อสำเร็จจะทำการเปิด Server แบบนี้ :
  ![MPU6050](https://drive.google.com/uc?export=view&id=1KMCUwgaPesantZ9zeK2KS2lQS6xCsXBc)

### 6. จากนั้นทำการเปิด Node-red
- เปิด Command Prompt หรือ PowerShell แล้วรันคำสั่ง:
  ```bash
  node-red
- จากนั้นเปิดผ่านเว็ป
  ```bash
  https://127.0.0.1:1880
- หน้าตาเปิด node-red
  ![node-red](https://drive.google.com/uc?export=view&id=1IDRekTcQcaSAoKrvrcteqVBN_RZ-BnI3)

### 7. ทำการ Import โปรเจ็คงานของเราคลิ้กตามรูปได้
- ![Import](https://drive.google.com/uc?export=view&id=1unBWQ8o5hnL_itjAL5nkZgbtBt8Yv_Xt)
- ![Import](https://drive.google.com/uc?export=view&id=18PAq07j-rD-47Wp-eHWZFOwr2G13wwoM)
- ![คำอธิบายภาพ](https://drive.google.com/uc?export=view&id=1mcpAeXC7fyAyx5RIGUnaD98nI3wcCbAk)
- ![คำอธิบายภาพ](https://drive.google.com/uc?export=view&id=1hPcaF_FQwJpCmNHZ195-aUG210uJotMM)

### 8. เราจะได้หน้าตา node-red ที่ทำไว้ในแต่ละ Node กด Deploy เพื่อเริ่มการทำงาน
- ![คำอธิบายภาพ](https://drive.google.com/uc?export=view&id=1Ju2lAeZGJFcJ_X1Y75xG1KNQiKK-v6km)

### 9.ทำการเปิด Dashboard ตามรูปภาพ
-  ![คำอธิบายภาพ](https://drive.google.com/uc?export=view&id=1uXJ7eudVE8j5SDmiASsok_ZQcIO1QqSe)
-  ![คำอธิบายภาพ](https://drive.google.com/uc?export=view&id=1h131MUQOZu2wCRKzBGb_a7_84axIH6Ii)
-  ![คำอธิบายภาพ](https://drive.google.com/uc?export=view&id=1h131MUQOZu2wCRKzBGb_a7_84axIH6Ii)



  


