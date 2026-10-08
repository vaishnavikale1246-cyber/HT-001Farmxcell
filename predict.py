import tensorflow as tf
import numpy as np
from pathlib import Path
from PIL import Image, ImageOps

# ==============================
# LOAD TRAINED MODEL
# ==============================

MODEL_PATH = Path(__file__).resolve().parent / "models" / "disease_model.keras"
model = None


def get_model():
    """Load the large TensorFlow model only when a prediction is requested."""
    global model
    if model is None:
        model = tf.keras.models.load_model(MODEL_PATH)
    return model

# ==============================
# CLASS NAMES
# ==============================

class_names = [
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus'
]

# ==============================
# PREDICT DISEASE
# ==============================

def predict_disease(image_source):
    """Predict from a path or a readable uploaded-file stream."""
    with Image.open(image_source) as uploaded_image:
        image = ImageOps.exif_transpose(uploaded_image).convert("RGB")
        image = image.resize((224, 224))
        image_array = np.asarray(image, dtype=np.float32)

    # Add batch dimension
    image_array = np.expand_dims(image_array, axis=0)

    # Predict
    predictions = get_model().predict(image_array, verbose=0)

    # Get highest probability
    predicted_index = np.argmax(predictions[0])

    # Get disease name
    disease = class_names[predicted_index]

    # Get confidence
    confidence = float(predictions[0][predicted_index]) * 100

    return disease, confidence
if __name__ == "__main__":

    image_path = "test_leaf.jpg"

    disease, confidence = predict_disease(image_path)

    print("================================")
    print("Disease:", disease)
    print("Confidence:", round(confidence, 2), "%")
    print("================================")
