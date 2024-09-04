<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Object Detection using Cogniflow</title>
    <style>
        /* CSS styling as previously defined */
        body {
            font-family: 'IBM Plex Sans Thai', sans-serif;
            background-color: #f4f7f9;
            color: #333;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }

        h1 {
            color: #579fec;
            font-size: 2rem;
            margin-bottom: 20px;
        }

        video, img {
            width: 100%;
            max-width: 400px;
            border: 3px solid #579fec;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }

        input[type="file"], button {
            background-color: #579fec;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s, box-shadow 0.3s;
            margin-bottom: 20px;
        }

        input[type="file"] {
            border: 2px dashed #579fec;
            background-color: #fff;
        }

        button:hover, input[type="file"]:hover {
            background-color: #417bbf;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }

        h2 {
            font-size: 1.5rem;
            color: #333;
            margin-bottom: 10px;
        }

        pre {
            background-color: #e6f0f9;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            overflow-x: auto;
            max-width: 100%;
        }
    </style>
</head>
<body>
    <h1>ถ่ายรูปหรือโหลดรูปเพื่อวิเคราะห์ว่าคืออะไร</h1>
    
    <video id="video" autoplay></video>
    <button id="captureButton">ถ่ายภาพ</button>

    <input type="file" id="imageUpload" accept="image/*">
    <button id="uploadButton">อัปโหลดภาพ</button>

    <h2>รูปที่เลือก:</h2>
    <img id="selectedImage" src="" alt="Selected Image">

    <h2>ผลลัพท์:</h2>
    <pre id="result"></pre>

    <script>
        const video = document.getElementById('video');
        const captureButton = document.getElementById('captureButton');
        const imageUpload = document.getElementById('imageUpload');
        const uploadButton = document.getElementById('uploadButton');
        const selectedImage = document.getElementById('selectedImage');
        const canvas = document.createElement('canvas');

        // Access the camera
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
            })
            .catch(error => {
                console.error('Error accessing the camera:', error);
            });

        // Capture image from video stream
        captureButton.addEventListener('click', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            const base64Image = canvas.toDataURL('image/jpeg').split(',')[1];
            selectedImage.src = canvas.toDataURL('image/jpeg');
            detectObjects(base64Image);
        });

        // Upload image from file input
        uploadButton.addEventListener('click', () => {
            const file = imageUpload.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onloadend = function() {
                    const base64Image = reader.result.split(',')[1];
                    selectedImage.src = reader.result;
                    detectObjects(base64Image);
                };
                reader.readAsDataURL(file);
            } else {
                alert('Please select an image file first.');
            }
        });

        // Function to send image for object detection
        function detectObjects(base64Image) {
            fetch('https://predict.cogniflow.ai/image/object-detection/detect/abc1226a-ebd1-ff05-22e3-aff01d32bc77', {
                method: 'POST',
                headers: {
                    accept: 'application/json',
                    'Content-Type': 'application/json',
                    'x-api-key': '8eabc609-b0ad-4f92-a685-7ccf42831666'
                },
                body: JSON.stringify({
                    "format": "jpeg",
                    "base64_image": base64Image,
                    "confidence_threshold": 0,
                    "normalize_boxes": false
                })
            })
            .then(response => response.json())
            .then(data => {
                const resultElement = document.getElementById('result');
                resultElement.innerHTML = ''; // Clear previous results
                
                const categoryCounts = {}; // Object to hold count and max confidence of each category
        
                if (data.result && data.result.length > 0) {
                    data.result.forEach(detection => {
                        const category = detection.category;
                        const confidence = detection.confidence_score;
                        if (!categoryCounts[category]) {
                            categoryCounts[category] = { count: 0, maxConfidence: 0 };
                        }
                        categoryCounts[category].count += 1;
                        if (confidence > categoryCounts[category].maxConfidence) {
                            categoryCounts[category].maxConfidence = confidence;
                        }
                    });
        
                    for (const [category, { count, maxConfidence }] of Object.entries(categoryCounts)) {
                        const resultItem = document.createElement('div');
                        resultItem.textContent = `หมวดหมู่: ${category}, จำนวน: ${count}, ความถูกต้องสูงสุด: ${(maxConfidence * 100).toFixed(2)}%`;
                        resultElement.appendChild(resultItem);
                    }
                } else {
                    resultElement.textContent = 'No objects detected.';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const resultElement = document.getElementById('result');
                resultElement.textContent = 'An error occurred while detecting objects. Please try again later.';
            });
        }
        
    </script>
</body>
</html>
