import cv2
import numpy as np
import pickle
import os
from datetime import datetime

class FaceDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.face_data_file = 'fars\\data\\processed\\face_data.pkl'
        self.model_file = 'fars\\data\\processed\\face_model.yml'
        self.load_data()

    def load_data(self):
        if os.path.exists(self.face_data_file):
            with open(self.face_data_file, 'rb') as f:
                self.label_dict = pickle.load(f)
        else:
            self.label_dict = {'labels': [], 'label_ids': {}, 'next_id': 0}
        
        if os.path.exists(self.model_file):
            self.recognizer.read(self.model_file)

    def save_data(self):
        with open(self.face_data_file, 'wb') as f:
            pickle.dump(self.label_dict, f)
        self.recognizer.write(self.model_file)

    def train_face(self):
        # Get label from user
        label = input("Enter the name/label for this face: ")
        
        # Assign ID to label if new
        if label not in self.label_dict['label_ids']:
            self.label_dict['label_ids'][label] = self.label_dict['next_id']
            self.label_dict['next_id'] += 1
        
        label_id = self.label_dict['label_ids'][label]
        faces = []
        labels = []
        
        cap = cv2.VideoCapture(0)
        count = 0
        max_samples = 100  # Number of samples to collect
        
        print("Collecting face samples. Please move your face slightly to capture different angles.")
        
        while count < max_samples:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected_faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Draw rectangle around detected faces
            for (x, y, w, h) in detected_faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            cv2.imshow('Collecting Samples - Press SPACE to capture', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' ') and len(detected_faces) == 1:
                # Get the face ROI (Region of Interest)
                (x, y, w, h) = detected_faces[0]
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (100, 100))
                
                faces.append(face_roi)
                labels.append(label_id)
                count += 1
                print(f"Captured sample {count}/{max_samples}")
        
        cap.release()
        cv2.destroyAllWindows()
        
        if faces:
            print("Training model...")
            # Update existing model
            self.recognizer.update(faces, np.array(labels))
            self.label_dict['labels'].append(label)
            self.save_data()
            print(f"Training completed! Total labels in database: {set(self.label_dict['labels'])}")
        else:
            print("No faces were captured. Please try again.")

    def compare_face(self):
        if not self.label_dict['labels']:
            print("No faces in database. Please train some faces first.")
            return
        
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Draw rectangle around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            cv2.imshow('Press SPACE to recognize or Q to quit', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                if len(faces) == 0:
                    print("No face detected. Please try again.")
                    continue
                
                results = []
                for (x, y, w, h) in faces:
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (100, 100))
                    
                    try:
                        label_id, confidence = self.recognizer.predict(face_roi)
                        
                        # Find label name from id
                        label_name = None
                        for name, id_ in self.label_dict['label_ids'].items():
                            if id_ == label_id:
                                label_name = name
                                break
                        
                        if confidence < 100:  # Lower confidence is better
                            results.append(f"Match found: {label_name} (Confidence: {confidence:.2f})")
                        else:
                            results.append("No match found (confidence too low)")
                    except Exception as e:
                        print(f"Error during recognition: {e}")
                
                for result in results:
                    print(result)
                break
        
        cap.release()
        cv2.destroyAllWindows()

def main():
    detector = FaceDetector()
    
    while True:
        print("\nFace Detection System")
        print("1. Train new face")
        print("2. Compare face")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            detector.train_face()
        elif choice == '2':
            detector.compare_face()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()