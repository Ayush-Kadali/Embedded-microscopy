#!/usr/bin/env python3
"""
Improved training script for better accuracy in prototype
Uses more data and better training parameters
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

# Improved CNN model with more capacity
def create_improved_model(num_classes, input_size=128):
    """Create a better CNN model with more capacity"""
    model = keras.Sequential([
        layers.Input(shape=(input_size, input_size, 3)),

        # Block 1
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        layers.Dropout(0.25),

        # Block 2
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        layers.Dropout(0.25),

        # Block 3
        layers.Conv2D(128, 3, padding='same', activation='relu'),
        layers.Conv2D(128, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        layers.Dropout(0.25),

        # Block 4
        layers.Conv2D(256, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.5),

        # Dense layers
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
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


def load_images_from_folder(folder, max_per_class=500, img_size=128):
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
        image_files = list(class_dir.glob('*.png'))
        if max_per_class:
            image_files = image_files[:max_per_class]

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
    logger.info("Starting IMPROVED classifier training...")
    logger.info("=" * 80)

    # Improved Parameters
    IMG_SIZE = 128          # Larger for better detail (was 64)
    MAX_PER_CLASS = 500     # More images (was 100)
    EPOCHS = 25             # More training (was 10)
    BATCH_SIZE = 32

    logger.info(f"Training parameters:")
    logger.info(f"  Image size: {IMG_SIZE}x{IMG_SIZE}")
    logger.info(f"  Max per class: {MAX_PER_CLASS}")
    logger.info(f"  Epochs: {EPOCHS}")
    logger.info(f"  Batch size: {BATCH_SIZE}")
    logger.info("=" * 80)

    # Load training data
    logger.info("\nLoading training images...")
    train_dir = 'datasets/raw/dataset_pm/training'

    if not Path(train_dir).exists():
        logger.error(f"Training directory not found: {train_dir}")
        return 1

    X, y, class_names = load_images_from_folder(
        train_dir,
        max_per_class=MAX_PER_CLASS,
        img_size=IMG_SIZE
    )

    logger.info(f"\nLoaded {len(X)} images across {len(class_names)} classes")
    logger.info(f"Class names: {class_names}")

    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    logger.info(f"\nTraining samples: {len(X_train)}")
    logger.info(f"Validation samples: {len(X_val)}")

    # Create improved model
    logger.info("\nCreating improved model...")
    model = create_improved_model(num_classes=len(class_names), input_size=IMG_SIZE)

    logger.info(f"Model created with {model.count_params():,} parameters")

    # Data augmentation for training
    data_augmentation = keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.2),
        layers.RandomTranslation(0.1, 0.1),
    ])

    # Augment training data
    logger.info("\nAugmenting training data...")
    X_train_aug = data_augmentation(X_train, training=True)

    # Train model
    logger.info(f"\nTraining for {EPOCHS} epochs...")
    logger.info("=" * 80)

    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            verbose=1,
            min_lr=0.00001
        ),
        keras.callbacks.ModelCheckpoint(
            'models/best_model_checkpoint.keras',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
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
    logger.info("\n" + "=" * 80)
    logger.info("Evaluating model...")
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    logger.info(f"Validation accuracy: {val_acc*100:.2f}%")
    logger.info(f"Validation loss: {val_loss:.4f}")

    # Per-class accuracy
    logger.info("\nComputing per-class accuracy...")
    y_pred = np.argmax(model.predict(X_val, verbose=0), axis=1)

    for i, class_name in enumerate(class_names):
        mask = y_val == i
        if mask.sum() > 0:
            acc = (y_pred[mask] == i).mean()
            logger.info(f"  {class_name}: {acc*100:.1f}% ({mask.sum()} samples)")

    # Save model
    os.makedirs('models', exist_ok=True)

    # Save Keras model
    model_path = 'models/plankton_classifier.keras'
    model.save(model_path)
    logger.info(f"\n✅ Saved Keras model to {model_path}")

    # Save class names
    class_names_path = 'models/class_names.pkl'
    with open(class_names_path, 'wb') as f:
        pickle.dump(class_names, f)
    logger.info(f"✅ Saved class names to {class_names_path}")

    # Save metadata
    metadata = {
        'num_classes': len(class_names),
        'class_names': class_names,
        'input_size': IMG_SIZE,
        'accuracy': float(val_acc),
        'num_params': model.count_params(),
        'training_samples': len(X_train),
        'validation_samples': len(X_val),
        'epochs_trained': len(history.history['loss']),
        'max_per_class': MAX_PER_CLASS
    }

    metadata_path = 'models/model_metadata.pkl'
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    logger.info(f"✅ Saved metadata to {metadata_path}")

    # Convert to TFLite for deployment
    logger.info("\nConverting to TFLite...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    tflite_path = 'models/plankton_classifier.tflite'
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    logger.info(f"✅ Saved TFLite model to {tflite_path}")

    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("🎉 TRAINING COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"Validation Accuracy: {val_acc*100:.2f}%")
    logger.info(f"Classes: {len(class_names)}")
    logger.info(f"Training samples: {len(X_train)}")
    logger.info(f"Model parameters: {model.count_params():,}")
    logger.info(f"Keras model size: ~{os.path.getsize(model_path) / 1024 / 1024:.1f} MB")
    logger.info(f"TFLite model size: ~{os.path.getsize(tflite_path) / 1024:.1f} KB")
    logger.info("=" * 80)

    return 0


if __name__ == '__main__':
    exit(main())
