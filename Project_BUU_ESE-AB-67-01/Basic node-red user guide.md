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
   - 3.1. ติดตั้งผ่าน Cmd หรือ Terminal วิธีนี้สามารถติดตั้งได้ง่าย
     ```bash
     npm install @flowfuse/node-red-dashboard-2-ui-flowviewer @flowfuse/node-red-dashboard-2-ui-iframe @flowfuse/node-red-dashboard-2-ui-led @flowfuse/node-red-dashboard
   - หลังจากติดตั้ง Node แล้ว คุณสามารถ รีสตาร์ท Node-RED เพื่อให้ Node ใหม่ทำงานได้:
     ```bash
     node-red-stop
     node-red-start
   - 3.2. ติดตั้งผ่าน Node-RED Palette Manager
      - คลิกที่ Menu (มุมขวาบน) แล้วเลือก Manage palette
      - ในแท็บ Install ให้ค้นหา Node ที่ต้องการ เช่น @flowfuse/node-red-dashboard-2-ui-flowviewer หรือ @flowfuse/node-red-dashboard
      - คลิก Install เพื่อติดตั้ง Node ดังกล่าว
   - 3.3. สามารถอัปโหลด node ของเราเองได้โดยเป็น File.tgz
      - ตัวอย่างไฟล์ที่ Custom เอง library ที่สร้างขึ้น ให้ดาวโหลดตรงนี้
     ```bash
     https://github.com/rextambunx/rextambunx.github.io/blob/master/Project_BUU_ESE-AB-67-01/node-red-contrib-project_buu_ese_ab_67_01-1.0.0.tgz

   - เมื่อโหลดเสร็จสิ้นแล้วให้ทำตามขั้นตอนนี้
      -   ติดตั้งผ่าน Node-RED Palette Manager
     ![My Diagram](https://drive.google.com/uc?export=view&id=1MACy03UTRJPSdoq-QDYjDB3zTbDkW1Gi)
     ![Node-RED Flow Example](https://drive.google.com/uc?export=view&id=1iQ6PVYbLXW612QArWKGkzBiOGSiD8LXV)
      -   ทำการติดตั้ง upload ไฟล์ node ที่ custom ขึ้นมาโดยไปดาวโหลดมาจากหัวข้อ 3.3.    
     ![Node-RED Dashboard](https://drive.google.com/uc?export=view&id=1mroLjldpK7E0T374p3Ry4c5O1aDiv7Rb)
      -   จากนั้นกด Upload แล้วไปดูที่ node ว่ามี node ใหม่ที่ติดตั้งหรือไม่
     ![Node-RED Machine Learning Integration](https://drive.google.com/uc?export=view&id=1zYHv35Y9sUgBALLKiiLqnFrS66oJyv5O)
     ![MPU6050 Sensor Setup](https://drive.google.com/uc?export=view&id=1ODgzqw5zMZQp61do5wWIJueeKouHj9OQ)
     ![System Architecture](https://drive.google.com/uc?export=view&id=1txCB44hiOdcODbfaWuB3NA35UiHovvep)

 ###  4. ตัวอย่าง Flow พื้นฐาน
        [Inject] --ส่งข้อความ--> [Function] --ประมวลผล--> [Debug]
   - โดยที่ในตัวของ Fucntion node จะเขียน code javascrip ตามนี้:
        ```bash
        msg.payload = "สวัสดี Node-RED!";
        return msg;

   - ![Data to Google Sheet](https://drive.google.com/uc?export=view&id=11bPI87m7TqRBLt8lmwqP9FZeXNZK4ReX)

 ###  5. ทาง Project Project_BUU_ESE-AB-67-01 ได้ทำการสร้าง Flow ที่ทำไว้เรียบร้อยเเล้ว (ส่วนเพิ่มเติม)
   - คลิกที่เมนูด้านขวาบน (สามขีด) > Import
   - จากนนั้นวาง Flow ได้เลยโดยใช้ .js
   -    ```bash
      [
    {
        "id": "6d9825bd727346a7",
        "type": "tab",
        "label": "Flow 1",
        "disabled": false,
        "info": "",
        "env": []
    },
    {
        "id": "d69f7de6b0c12db5",
        "type": "inject",
        "z": "6d9825bd727346a7",
        "name": "",
        "props": [
            {
                "p": "payload"
            },
            {
                "p": "topic",
                "vt": "str"
            }
        ],
        "repeat": "",
        "crontab": "",
        "once": false,
        "onceDelay": 0.1,
        "topic": "",
        "payload": "",
        "payloadType": "date",
        "x": 340,
        "y": 120,
        "wires": [
            [
                "335c381059489c90"
            ]
        ]
    },
    {
        "id": "335c381059489c90",
        "type": "function",
        "z": "6d9825bd727346a7",
        "name": "function 19",
        "func": "msg.payload = \"สวัสดี Node-RED!\";\nreturn msg;\n",
        "outputs": 1,
        "timeout": 0,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 550,
        "y": 160,
        "wires": [
            [
                "4508d6612db1ab9f"
            ]
        ]
    },
    {
        "id": "4508d6612db1ab9f",
        "type": "debug",
        "z": "6d9825bd727346a7",
        "name": "debug 12",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "false",
        "statusVal": "",
        "statusType": "auto",
        "x": 740,
        "y": 120,
        "wires": []
    },
    {
        "id": "2fb5190276df1285",
        "type": "project_buu_ese_ab_67_01",
        "z": "6d9825bd727346a7",
        "x": 780,
        "y": 300,
        "wires": [
            []
        ]
    },
    {
        "id": "68635863cbfc6f7b",
        "type": "comment",
        "z": "6d9825bd727346a7",
        "name": "",
        "info": "",
        "x": 520,
        "y": 360,
        "wires": []
    }
    ]

-   ในส่วนนี้จะถึงการ import ออกมาใช้ต่างๆ
  
 ###  5. 🔐 การเชื่อมต่อกับ MQTT Broker
 -   เพิ่ม Node mqtt in หรือ mqtt out
 -   ตั้งค่าเซิร์ฟเวอร์ เช่น mqtt://localhost:1883
 -   กำหนด Topic ที่ต้องการรับ/ส่ง เช่น sensor/data
 -   ![Node-RED Control Panel](https://drive.google.com/uc?export=view&id=1GFX4hkrk_BmADkUBi5aWo_axM00zmtpg)

 ###  6. 🧩 วิดิโอสอนการใช้งานเบื้องต้น
 -   🎥 [ดูวิดีโอการทำงานของ Node-RED](https://drive.google.com/file/d/1j1FHAE96QHWSOKCWtZYmgzIZBcFPKJBw/view?usp=sharing)

