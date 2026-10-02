import requests
from services.face_service import FaceService

IMAGE_URL = "http://res.cloudinary.com/do64ymnem/image/upload/v1783104817/event_images/photographer_b8383b76-1bdc-44be-8c81-255b78932ffa/event_990dc916-37fd-49d1-a050-86ff9a298352/file_svetmb.webp"

face_service = FaceService()

print("Downloading image...")

response = requests.get(IMAGE_URL)

print("Status:", response.status_code)
print("Bytes:", len(response.content))

image = face_service.bytes_to_image(response.content)

print("Image:", image.shape)

faces = face_service.detect_faces(image)

print("FINAL FACE COUNT:", len(faces))

for i, face in enumerate(faces):
    print("Face:", i + 1)
    print("BBox:", face.bbox)
    print("Score:", face.det_score)
    print("Embedding:", face.embedding.shape)