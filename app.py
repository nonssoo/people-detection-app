import os
import time
import cv2
import torch
import numpy as np
from flask import Flask, Response, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from sort import Sort

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load YOLO Model
try:
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    model.eval()
    print("✅ YOLO model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading YOLO model: {e}")
    raise

# Initialize SORT Tracker
tracker = Sort()

@app.route('/detect', methods=['POST'])
def detect_objects():
    if 'frame' not in request.files:
        return jsonify({'error': 'No frame uploaded'}), 400
    
    file = request.files['frame']
    if file.filename == '':
        return jsonify({'error': 'No frame selected'}), 400

    # Read image file
    img_bytes = file.read()
    img_np = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    
    if frame is None:
        return jsonify({'error': 'Could not decode image'}), 400
    
    # Convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Perform detection
    results = model(rgb_frame)
    
    # Format detections for response
    detections = []
    for box in results.xyxy[0].cpu().numpy():
        x1, y1, x2, y2, conf, cls = box
        detections.append({
            'x1': float(x1),
            'y1': float(y1),
            'x2': float(x2),
            'y2': float(y2),
            'conf': float(conf),
            'cls': int(cls)
        })
    
    return jsonify(detections)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Process based on file type
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        # Image processing
        img = cv2.imread(file_path)
        results = model(img)
        
        person_count = 0
        for box in results.xyxy[0].cpu().numpy():
            x1, y1, x2, y2, conf, cls = box
            if int(cls) == 0:  # Person class
                person_count += 1
        
        return jsonify({
            'person_count': person_count,
            'processed_file': f'/download/{filename}'
        })
        
    elif filename.lower().endswith(('.mp4', '.avi', '.mov')):
        # Video processing
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return jsonify({'error': 'Unable to open video'}), 400

        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + filename)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS),
                            (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                             int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        unique_person_ids = set()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)
            detections = []

            for box in results.xyxy[0].cpu().numpy():
                x1, y1, x2, y2, conf, cls = box
                if int(cls) == 0:  # Person class
                    detections.append([x1, y1, x2, y2, conf])

            trackers = tracker.update(np.array(detections) if detections else np.empty((0, 5)))

            for track in trackers:
                x1, y1, x2, y2, track_id = track.astype(int)
                unique_person_ids.add(track_id)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'ID {track_id}', (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.putText(frame, f'Unique People: {len(unique_person_ids)}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            out.write(frame)

        cap.release()
        out.release()
        
        return jsonify({
            'person_count': len(unique_person_ids),
            'processed_file': f'/download/processed_{filename}'
        })
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)