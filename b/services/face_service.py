import cv2
import numpy as np
import insightface


class FaceService:

    def __init__(self):
        self.app = insightface.app.FaceAnalysis(
            name="buffalo_l"
        )

        self.app.prepare(
            ctx_id=-1,          # CPU
            det_size=(640, 640)
        )

    def detect_faces(self, image_bytes):

        image = np.frombuffer(image_bytes, np.uint8)

        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        faces = self.app.get(image)

        return faces

    def generate_embedding(self, face):

        return face.embedding.tolist()

    @staticmethod
    def bytes_to_image(image_bytes: bytes):

        image = cv2.imdecode(
            np.frombuffer(image_bytes, np.uint8),
            cv2.IMREAD_COLOR
        )

        if image is None:
            raise ValueError("Invalid image")

        return image