#!/usr/bin/env python3
"""
BEST POSSIBLE MODEL - Transfer Learning with EfficientNetB0
No compromises - train for as long as needed for maximum accuracy
"""

import os
import numpy as np
import cv2
from pathlib import Path
import pickle
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import EfficientNetB0
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_best_model(num_classes, input_size=224):
    """
    Create best possible model using transfer learning
    EfficientNetB0 pre-trained on ImageNet
    """
    logger.info("Creating model with EfficientNetB0 transfer learning...")

    # Load pre-trained EfficientNetB0 (trained on ImageNet)
    base_model = EfficientNetB0(
        include_top=False,
        weights='imagenet',
        input_shape=(input_size, input_size, 3),
        pooling='avg'
    )

    # Freeze base model initially - we'll unfreeze later for fine-tuning
    base_model.trainable = False

    # Build complete model
    model = keras.Sequential([
        base_model,
        layers.Dropout(0.5),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model, base_model


def load_all_images(folder, img_size=224):
    """
    Load ALL available images - no limits!
    """
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

        # Get ALL image files - no limits
        image_files = list(class_dir.glob('*.png'))

        logger.info(f"Loading {len(image_files)} images for class '{class_name}'")

        for img_file in image_files:
            try:
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
    logger.info("=" * 80)
    logger.info("TRAINING BEST POSSIBLE MODEL - NO COMPROMISES")
    logger.info("=" * 80)

    # Best parameters for transfer learning
    IMG_SIZE = 224          # Standard for transfer learning
    BATCH_SIZE = 16         # Smaller batch for better gradients
    PHASE1_EPOCHS = 30      # Train top layers
    PHASE2_EPOCHS = 50      # Fine-tune all layers

    logger.info(f"\nTraining parameters:")
    logger.info(f"  Image size: {IMG_SIZE}x{IMG_SIZE}")
    logger.info(f"  Batch size: {BATCH_SIZE}")
    logger.info(f"  Phase 1 (frozen base): {PHASE1_EPOCHS} epochs")
    logger.info(f"  Phase 2 (fine-tuning): {PHASE2_EPOCHS} epochs")
    logger.info(f"  Total epochs: {PHASE1_EPOCHS + PHASE2_EPOCHS}")
    logger.info(f"  Using ALL available images (no limits)")
    logger.info("=" * 80)

    # Load ALL training data
    logger.info("\nLoading ALL training images...")
    train_dir = 'datasets/raw/dataset_pm/training'

    if not Path(train_dir).exists():
        logger.error(f"Training directory not found: {train_dir}")
        return 1

    X, y, class_names = load_all_images(train_dir, img_size=IMG_SIZE)

    logger.info(f"\nLoaded {len(X)} images across {len(class_names)} classes")
    logger.info(f"Class names: {class_names}")

    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    logger.info(f"\nTraining samples: {len(X_train)}")
    logger.info(f"Validation samples: {len(X_val)}")

    # Create advanced data augmentation
    logger.info("\nSetting up data augmentation...")
    data_augmentation = keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.3),
        layers.RandomZoom(0.2),
        layers.RandomTranslation(0.1, 0.1),
        layers.RandomContrast(0.2),
    ])

    # Create model
    logger.info("\nCreating transfer learning model...")
    model, base_model = create_best_model(num_classes=len(class_names), input_size=IMG_SIZE)

    logger.info(f"Total parameters: {model.count_params():,}")
    logger.info(f"Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")

    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            verbose=1,
            min_lr=0.000001
        ),
        keras.callbacks.ModelCheckpoint(
            'models/best_model_checkpoint.keras',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]

    # PHASE 1: Train with frozen base
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1: Training top layers (base frozen)")
    logger.info("=" * 80)

    # Augment training data
    X_train_aug = data_augmentation(X_train, training=True)

    history1 = model.fit(
        X_train_aug, y_train,
        batch_size=BATCH_SIZE,
        epochs=PHASE1_EPOCHS,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        verbose=1
    )

    # Evaluate after phase 1
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    logger.info(f"\nPhase 1 Results:")
    logger.info(f"  Validation accuracy: {val_acc*100:.2f}%")
    logger.info(f"  Validation loss: {val_loss:.4f}")

    # PHASE 2: Fine-tune all layers
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2: Fine-tuning all layers (base unfrozen)")
    logger.info("=" * 80)

    # Unfreeze base model
    base_model.trainable = True

    # Recompile with lower learning rate for fine-tuning
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),  # 10x lower
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    logger.info(f"Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")

    # Continue training with all layers unfrozen
    history2 = model.fit(
        X_train_aug, y_train,
        batch_size=BATCH_SIZE,
        epochs=PHASE2_EPOCHS,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        verbose=1
    )

    # Final evaluation
    logger.info("\n" + "=" * 80)
    logger.info("FINAL EVALUATION")
    logger.info("=" * 80)

    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    logger.info(f"Final validation accuracy: {val_acc*100:.2f}%")
    logger.info(f"Final validation loss: {val_loss:.4f}")

    # Per-class accuracy
    logger.info("\nPer-class accuracy:")
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
        'phase1_epochs': len(history1.history['loss']),
        'phase2_epochs': len(history2.history['loss']),
        'total_epochs': len(history1.history['loss']) + len(history2.history['loss']),
        'architecture': 'EfficientNetB0 Transfer Learning'
    }

    metadata_path = 'models/model_metadata.pkl'
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    logger.info(f"✅ Saved metadata to {metadata_path}")

    # Convert to TFLite
    logger.info("\nConverting to TFLite for Raspberry Pi...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    tflite_path = 'models/plankton_classifier.tflite'
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    logger.info(f"✅ Saved TFLite model to {tflite_path}")

    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("🎉 TRAINING COMPLETE - BEST MODEL READY!")
    logger.info("=" * 80)
    logger.info(f"Final Accuracy: {val_acc*100:.2f}%")
    logger.info(f"Architecture: EfficientNetB0 Transfer Learning")
    logger.info(f"Total Parameters: {model.count_params():,}")
    logger.info(f"Training Samples: {len(X_train)}")
    logger.info(f"Total Epochs: {metadata['total_epochs']}")
    logger.info(f"Keras Model: ~{os.path.getsize(model_path) / 1024 / 1024:.1f} MB")
    logger.info(f"TFLite Model: ~{os.path.getsize(tflite_path) / 1024:.1f} KB")
    logger.info("=" * 80)

    return 0


if __name__ == '__main__':
    exit(main())
