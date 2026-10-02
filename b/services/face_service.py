import cv2
import numpy as np
import insightface


class FaceService:

    def __init__(self):

        self.app = insightface.app.FaceAnalysis(
            name="buffalo_l"
        )

        self.app.prepare(
            ctx_id=-1,
            det_size=(640, 640)
        )

    def detect_faces(self, image):

        print("=" * 60)
        print("INSIGHTFACE DEBUG")

        print("Image shape:", image.shape)
        print("Image dtype:", image.dtype)
        print("Image min:", image.min())
        print("Image max:", image.max())

        faces = self.app.get(image)

        print("Number of faces:", len(faces))

        for i, face in enumerate(faces):

            print(f"Face {i + 1}")
            print("  bbox:", face.bbox)
            print("  detection score:", face.det_score)
            print("  embedding shape:", face.embedding.shape)

        print("=" * 60)

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


face_service = FaceService()