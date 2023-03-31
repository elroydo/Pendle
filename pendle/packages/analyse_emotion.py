import cv2 as cv
from deepface import DeepFace

# Emotion recognition using Deepface
def get_dominant_emotion(frame):
    alpha_frame = cv.convertScaleAbs(frame, alpha=1.7, beta=0)
    
    try:
        # Emotional analysis
        emotion = DeepFace.analyze(alpha_frame, actions=['emotion'], silent=True)
        dominant_emotion = emotion[0]['dominant_emotion']
        return dominant_emotion
    
    except Exception as e:
        print(e)
        return None