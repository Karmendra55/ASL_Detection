from PIL import Image

import numpy as np
import cv2
import tensorflow as tf
import json

IMG_SIZE = (160, 160) 

class ASLClassifier:
    def __init__(self, model_path, class_map_path):
        self.model = tf.keras.models.load_model(str(model_path))
        with open(class_map_path, 'r') as f:
            self.class_names = json.load(f)

    @staticmethod
    def _preprocess(img):
        """
        Preprocess input image (PIL.Image, np.ndarray, or uploaded file) for model prediction.
        Ensures output is always (1, 160, 160, 3)
        """
        # If it's a PIL image
        if isinstance(img, Image.Image):
            img_array = np.array(img.convert("RGB"))
        # If it's a NumPy array (OpenCV BGR image)
        elif isinstance(img, np.ndarray):
            if img.ndim == 2:
                img_array = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 3:
                img_array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                raise ValueError(f"Unexpected number of channels: {img.shape[2]}")
        else:
            img_array = np.array(img)
            if img_array.ndim == 2:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            elif img_array.ndim == 3 and img_array.shape[2] == 4:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)

        img_resized = cv2.resize(img_array, (160, 160), interpolation=cv2.INTER_AREA)
        img_normalized = img_resized.astype(np.float32) / 255.0
        return np.expand_dims(img_normalized, axis=0)

    def predict(self, img):
        x = self._preprocess(img)
        probs = self.model.predict(x, verbose=0)[0]
        idx = int(np.argmax(probs))
        return {
            "label": self.class_names[idx],
            "index": idx,
            "confidence": float(probs[idx]),
            "probs": {self.class_names[i]: float(p) for i, p in enumerate(probs)}
        }
