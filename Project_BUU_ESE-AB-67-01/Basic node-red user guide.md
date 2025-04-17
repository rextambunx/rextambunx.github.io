# โปรเจ็กต์ของ Project_BUU_ESE-AB-67-01

## 📌 วิธีการใช้งาน node-red เบื้องต้น

### 1. 🧩 โครงสร้างพื้นฐานของ Node-RED
-  1. Flow – หน้าจอหลักสำหรับออกแบบการทำงาน
-  2. Node – บล็อกต่าง ๆ ที่ใช้ใน Flow (ลากจากด้านซ้าย)
-  3. Deploy – ปุ่มสีแดงมุมขวาบน กดเพื่อบันทึกและใช้งาน Flow
   <img src="https://drive.google.com/uc?export=view&id=100xmO36Ny5Sc0qi3kkQ3k9V30Qrk267A" alt="node-red" width="500"/>

### 2. ประเภท Node ที่ควรรู้เบื้องต้น
- inject – ใช้สำหรับป้อนข้อมูลเข้าสู่ Flow เช่น ส่งข้อความ หรือส่งค่าตามเวลา
- debug – แสดงค่าที่ถูกส่งผ่าน Node ต่าง ๆ ในหน้าต่าง Debug
  - ![Import](https://drive.google.com/uc?export=view&id=1JccaxXu_MCrL2Hbjbv8aPMjsFAow5Ou0)
  - ![Import](https://drive.google.com/uc?export=view&id=1L5ckpMvxCG9jcydbMQTQQaZdeooCc7Ap)
- function – เขียนโค้ด JavaScript เพื่อประมวลผลหรือแปลงค่าต่าง ๆ ตามต้องการ
  - ![Import](https://drive.google.com/uc?export=view&id=1TuUj-ybIhrPVt9eHO_VS8pbn-4_tR3T4)
- http in / http response – ใช้สำหรับสร้าง API เพื่อรับและตอบกลับข้อมูลผ่าน HTTP****
- mqtt in / mqtt out – ใช้เชื่อมต่อกับ MQTT Broker สำหรับรับหรือส่งข้อมูลแบบ publish/subscribe
  - ![Import](https://drive.google.com/uc?export=view&id=1NUQDtxilnhCjpip2Z5rNwd8Q24VBuyEl)
- chart / gauge – ใช้แสดงผลข้อมูลแบบกราฟ หรือ มาตรวัด บน Dashboard
  - ![Import](https://drive.google.com/uc?export=view&id=1VFavbBYwSg6GfpRtQs_q1SkQqkhQFkLe)
- ui node – กลุ่ม Node สำหรับสร้าง UI เช่น ปุ่ม, ตัวเลข, สวิทช์ บน Dashboard (ต้องติดตั้ง node-red-dashboard ก่อน)
### 3. วิธีติดตั้ง Node-RED Library (Nodes) เพิ่มเติมมี 2 วิธีคือ
   - 3.1 ติดตั้งผ่าน Cmd หรือ Terminal วิธีนี้สามารถติดตั้งได้ง่าย
     ```bash
     npm install @flowfuse/node-red-dashboard-2-ui-flowviewer @flowfuse/node-red-dashboard-2-ui-iframe @flowfuse/node-red-dashboard-2-ui-led @flowfuse/node-red-dashboard
   - หลังจากติดตั้ง Node แล้ว คุณสามารถ รีสตาร์ท Node-RED เพื่อให้ Node ใหม่ทำงานได้:
     ```bash
     node-red-stop
     node-red-start
   - 3.2 ติดตั้งผ่าน Node-RED Palette Manager
      - คลิกที่ Menu (มุมขวาบน) แล้วเลือก Manage palette
      - ในแท็บ Install ให้ค้นหา Node ที่ต้องการ เช่น @flowfuse/node-red-dashboard-2-ui-flowviewer หรือ @flowfuse/node-red-dashboard
      - คลิก Install เพื่อติดตั้ง Node ดังกล่าว
   - 3.3 สามารถอัปโหลด node ของเราเองได้โดยเป็น File.tgz
      - ตัวอย่างไฟล์ที่ Custom เอง library ที่สร้างขึ้น
     ```bash
     
