#!/usr/bin/env python3
"""
Quick training script for plankton classification
Uses a simple CNN model that can be trained quickly
"""

import os
import numpy as np
import cv2
from pathlib import Path
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple and fast CNN model
def create_model(num_classes, input_size=64):
    """Create a lightweight CNN model"""
    model = keras.Sequential([
        layers.Input(shape=(input_size, input_size, 3)),

        # Block 1
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        layers.Dropout(0.25),

        # Block 2
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        layers.Dropout(0.25),

        # Block 3
        layers.Conv2D(128, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.5),

        # Output
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model


def load_images_from_folder(folder, max_per_class=100, img_size=64):
    """Load images from folder structure"""
    images = []
    labels = []
    class_names = []

    # Get all class directories
    class_dirs = [d for d in Path(folder).iterdir() if d.is_dir() and d.name != 'desktop.ini']
    class_dirs = sorted(class_dirs)

    logger.info(f"Found {len(class_dirs)} classes")

    for class_idx, class_dir in enumerate(class_dirs):
        class_name = class_dir.name
        class_names.append(class_name)

        # Get image files
        image_files = list(class_dir.glob('*.png'))[:max_per_class]

        logger.info(f"Loading {len(image_files)} images for class '{class_name}'")

        for img_file in image_files:
            try:
                # Load and resize image
                img = cv2.imread(str(img_file))
                if img is None:
                    continue

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (img_size, img_size))
                img = img.astype('float32') / 255.0

                images.append(img)
                labels.append(class_idx)
            except Exception as e:
                logger.warning(f"Failed to load {img_file}: {e}")
                continue

    return np.array(images), np.array(labels), class_names


def main():
    logger.info("Starting quick classifier training...")

    # Parameters
    IMG_SIZE = 64
    MAX_PER_CLASS = 100  # Limit for quick training
    EPOCHS = 10
    BATCH_SIZE = 32

    # Load training data
    logger.info("Loading training images...")
    train_dir = 'datasets/raw/dataset_pm/training'

    if not Path(train_dir).exists():
        logger.error(f"Training directory not found: {train_dir}")
        return 1

    X, y, class_names = load_images_from_folder(
        train_dir,
        max_per_class=MAX_PER_CLASS,
        img_size=IMG_SIZE
    )

    logger.info(f"Loaded {len(X)} images across {len(class_names)} classes")
    logger.info(f"Class names: {class_names}")

    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    logger.info(f"Training samples: {len(X_train)}")
    logger.info(f"Validation samples: {len(X_val)}")

    # Create model
    logger.info("Creating model...")
    model = create_model(num_classes=len(class_names), input_size=IMG_SIZE)

    logger.info(f"Model created with {model.count_params()} parameters")

    # Data augmentation for training
    data_augmentation = keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
    ])

    # Augment training data
    logger.info("Augmenting training data...")
    X_train_aug = data_augmentation(X_train, training=True)

    # Train model
    logger.info(f"Training for {EPOCHS} epochs...")

    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=3,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=2
        )
    ]

    history = model.fit(
        X_train_aug, y_train,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        verbose=1
    )

    # Evaluate
    logger.info("\nEvaluating model...")
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    logger.info(f"Validation accuracy: {val_acc*100:.2f}%")

    # Save model
    os.makedirs('models', exist_ok=True)

    # Save Keras model
    model_path = 'models/plankton_classifier.keras'
    model.save(model_path)
    logger.info(f"Saved Keras model to {model_path}")

    # Save class names
    class_names_path = 'models/class_names.pkl'
    with open(class_names_path, 'wb') as f:
        pickle.dump(class_names, f)
    logger.info(f"Saved class names to {class_names_path}")

    # Save metadata
    metadata = {
        'num_classes': len(class_names),
        'class_names': class_names,
        'input_size': IMG_SIZE,
        'accuracy': float(val_acc),
        'num_params': model.count_params()
    }

    metadata_path = 'models/model_metadata.pkl'
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    logger.info(f"Saved metadata to {metadata_path}")

    # Convert to TFLite for deployment
    logger.info("\nConverting to TFLite...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    tflite_path = 'models/plankton_classifier.tflite'
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    logger.info(f"Saved TFLite model to {tflite_path}")

    logger.info("\n" + "="*80)
    logger.info("TRAINING COMPLETE!")
    logger.info("="*80)
    logger.info(f"Validation Accuracy: {val_acc*100:.2f}%")
    logger.info(f"Classes: {len(class_names)}")
    logger.info(f"Model size: ~{os.path.getsize(tflite_path) / 1024:.1f} KB")
    logger.info("="*80)

    return 0


if __name__ == '__main__':
    exit(main())
