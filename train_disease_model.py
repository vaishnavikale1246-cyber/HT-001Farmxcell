import tensorflow as tf
from tensorflow.keras import layers, models
import os

# ==========================
# Dataset Path
# ==========================
DATASET_PATH = "dataset"
MODEL_PATH = "models/disease_model.keras"

# Create models folder if it doesn't exist
os.makedirs("models", exist_ok=True)

# ==========================
# Load Dataset
# ==========================
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_PATH,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(224, 224),
    batch_size=32
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_PATH,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(224, 224),
    batch_size=32
)

# Print class names
class_names = train_ds.class_names
print("\nDetected Classes:")
print(class_names)

# ==========================
# Improve Performance
# ==========================
AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# ==========================
# Build CNN Model
# ==========================
model = models.Sequential([

    layers.Rescaling(1./255, input_shape=(224, 224, 3)),

    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D(),

    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(),

    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D(),

    layers.Flatten(),

    layers.Dense(256, activation='relu'),

    layers.Dropout(0.5),

    layers.Dense(len(class_names), activation='softmax')
])

# ==========================
# Compile Model
# ==========================
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# ==========================
# Model Summary
# ==========================
model.summary()

# ==========================
# Train Model
# ==========================
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10
)

# ==========================
# Save Model
# ==========================
model.save(MODEL_PATH)

print("\n===================================")
print("Model Trained Successfully!")
print("Saved as:", MODEL_PATH)
print("===================================")