import cv2
import requests
from services.face_service import FaceService

URL = "https://res.cloudinary.com/do64ymnem/image/upload/v1783104817/event_images/photographer_b8383b76-1bdc-44be-8c81-255b78932ffa/event_990dc916-37fd-49d1-a050-86ff9a298352/file_svetmb.webp"

print("Downloading image...")

response = requests.get(URL, timeout=30)

print("Status:", response.status_code)
print("Size:", len(response.content))

image = FaceService.bytes_to_image(response.content)

print("Image shape:", image.shape)

print("Creating FaceService...")

face_service = FaceService()

print("Running InsightFace...")

faces = face_service.detect_faces(image)

print("Faces:", len(faces))