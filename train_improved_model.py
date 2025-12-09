#!/usr/bin/env python3
"""
Improved Plankton Classifier Training Script
Uses transfer learning with MobileNetV2 for better accuracy and Pi deployment

Expected improvement: 38% -> 75-85% accuracy
Training time: ~45-90 minutes on laptop
"""

import os
import sys
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.applications import MobileNetV2
from pathlib import Path
import pickle
import json
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

# Configuration
CONFIG = {
    'dataset_path': 'datasets/raw/dataset_pm/training',
    'model_name': 'plankton_mobilenet_v2',
    'img_size': 128,  # Increased from 64 for better accuracy
    'batch_size': 32,
    'epochs': 50,
    'learning_rate': 0.001,
    'fine_tune_epochs': 20,
    'fine_tune_lr': 0.0001,
    'max_samples_per_class': None,  # Use all available data
    'validation_split': 0.2,
    'seed': 42
}

print("=" * 80)
print("IMPROVED PLANKTON CLASSIFIER - TRAINING SCRIPT")
print("=" * 80)
print(f"\nConfiguration:")
for key, value in CONFIG.items():
    print(f"  {key}: {value}")
print("\n" + "=" * 80 + "\n")

# Set seeds for reproducibility
np.random.seed(CONFIG['seed'])
tf.random.set_seed(CONFIG['seed'])

# GPU configuration
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"✓ GPU detected: {gpus[0].name}")
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(f"GPU configuration error: {e}")
else:
    print("⚠ No GPU detected, training on CPU (will be slower)")

def load_dataset():
    """Load and prepare dataset with augmentation"""
    print("\n[1/6] Loading dataset...")

    dataset_path = Path(CONFIG['dataset_path'])
    if not dataset_path.exists():
        print(f"✗ Dataset not found at: {dataset_path}")
        print("  Please check the path in CONFIG['dataset_path']")
        sys.exit(1)

    # Get class names
    class_names = sorted([d.name for d in dataset_path.iterdir() if d.is_dir()])
    print(f"  Found {len(class_names)} classes: {class_names[:5]}...")

    # Load images and labels
    images = []
    labels = []
    samples_per_class = {cls: 0 for cls in class_names}

    for class_idx, class_name in enumerate(class_names):
        class_path = dataset_path / class_name
        image_files = list(class_path.glob('*.png')) + list(class_path.glob('*.jpg'))

        # Limit samples if configured
        if CONFIG['max_samples_per_class']:
            image_files = image_files[:CONFIG['max_samples_per_class']]

        for img_path in image_files:
            try:
                # Load and preprocess
                img = tf.keras.preprocessing.image.load_img(
                    img_path,
                    target_size=(CONFIG['img_size'], CONFIG['img_size'])
                )
                img_array = tf.keras.preprocessing.image.img_to_array(img)
                images.append(img_array)
                labels.append(class_idx)
                samples_per_class[class_name] += 1
            except Exception as e:
                print(f"  Warning: Failed to load {img_path}: {e}")
                continue

    print(f"\n  Loaded {len(images)} images total")
    print("\n  Samples per class:")
    for cls, count in samples_per_class.items():
        print(f"    {cls}: {count}")

    # Convert to numpy arrays
    X = np.array(images, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)

    # Normalize to [0, 1]
    X = X / 255.0

    print(f"\n  Dataset shape: {X.shape}")
    print(f"  Labels shape: {y.shape}")

    return X, y, class_names

def create_data_augmentation():
    """Create data augmentation pipeline"""
    return keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.3),
        layers.RandomZoom(0.2),
        layers.RandomContrast(0.2),
        layers.RandomBrightness(0.2),
    ], name='data_augmentation')

def create_model(num_classes, input_shape):
    """Create improved model with transfer learning"""
    print("\n[2/6] Building model architecture...")

    # Input
    inputs = layers.Input(shape=input_shape)

    # Data augmentation (applied during training only)
    augmentation = create_data_augmentation()
    x = augmentation(inputs)

    # Preprocessing for MobileNetV2
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)

    # MobileNetV2 backbone (pretrained on ImageNet)
    base_model = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Freeze initially

    x = base_model(x, training=False)

    # Custom classification head
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.3)(x)

    # Output layer
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = models.Model(inputs=inputs, outputs=outputs)

    print(f"\n  Architecture:")
    print(f"    Base: MobileNetV2 (ImageNet pretrained)")
    print(f"    Input size: {input_shape}")
    print(f"    Total parameters: {model.count_params():,}")
    print(f"    Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")

    return model, base_model

def create_callbacks(model_name):
    """Create training callbacks"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    callback_list = [
        # Save best model
        callbacks.ModelCheckpoint(
            f'models/{model_name}_best.keras',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),

        # Reduce learning rate on plateau
        callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        ),

        # Early stopping
        callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),

        # Log to CSV
        callbacks.CSVLogger(
            f'models/{model_name}_training_{timestamp}.csv'
        ),

        # TensorBoard
        callbacks.TensorBoard(
            log_dir=f'logs/{model_name}_{timestamp}',
            histogram_freq=1
        )
    ]

    return callback_list

def plot_training_history(history, model_name):
    """Plot training curves"""
    print("\n[5/6] Generating training plots...")

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Accuracy
    axes[0].plot(history.history['accuracy'], label='Training')
    axes[0].plot(history.history['val_accuracy'], label='Validation')
    axes[0].set_title('Model Accuracy', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Loss
    axes[1].plot(history.history['loss'], label='Training')
    axes[1].plot(history.history['val_loss'], label='Validation')
    axes[1].set_title('Model Loss', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'models/{model_name}_training_history.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: models/{model_name}_training_history.png")

    return fig

def evaluate_model(model, X_val, y_val, class_names, model_name):
    """Comprehensive model evaluation"""
    print("\n[6/6] Evaluating model...")

    # Predictions
    y_pred_probs = model.predict(X_val, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=1)

    # Accuracy
    accuracy = np.mean(y_pred == y_val)
    print(f"\n  ✓ Validation Accuracy: {accuracy*100:.2f}%")

    # Per-class accuracy
    print("\n  Per-class accuracy:")
    for i, class_name in enumerate(class_names):
        mask = y_val == i
        if mask.sum() > 0:
            class_acc = np.mean(y_pred[mask] == y_val[mask])
            print(f"    {class_name}: {class_acc*100:.1f}% ({mask.sum()} samples)")

    # Classification report
    print("\n  Classification Report:")
    report = classification_report(y_val, y_pred, target_names=class_names, digits=3)
    print(report)

    # Save report
    with open(f'models/{model_name}_classification_report.txt', 'w') as f:
        f.write(f"Validation Accuracy: {accuracy*100:.2f}%\n\n")
        f.write("Classification Report:\n")
        f.write(report)

    # Confusion matrix
    cm = confusion_matrix(y_val, y_pred)

    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix', fontsize=16, fontweight='bold')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f'models/{model_name}_confusion_matrix.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ Saved: models/{model_name}_confusion_matrix.png")

    # Confidence analysis
    confidences = np.max(y_pred_probs, axis=1)
    print(f"\n  Confidence Statistics:")
    print(f"    Mean: {np.mean(confidences)*100:.1f}%")
    print(f"    Median: {np.median(confidences)*100:.1f}%")
    print(f"    Min: {np.min(confidences)*100:.1f}%")
    print(f"    Max: {np.max(confidences)*100:.1f}%")

    return {
        'accuracy': accuracy,
        'report': report,
        'confusion_matrix': cm,
        'confidences': confidences
    }

def convert_to_tflite(model, model_name):
    """Convert model to TensorFlow Lite for Raspberry Pi"""
    print("\n  Converting to TensorFlow Lite...")

    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # Optimizations for edge deployment
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]

    tflite_model = converter.convert()

    # Save
    tflite_path = f'models/{model_name}.tflite'
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)

    # Get size
    size_kb = len(tflite_model) / 1024
    print(f"  ✓ TFLite model saved: {tflite_path} ({size_kb:.1f} KB)")

    return tflite_path

def main():
    """Main training pipeline"""

    # Load data
    X, y, class_names = load_dataset()

    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=CONFIG['validation_split'],
        stratify=y,
        random_state=CONFIG['seed']
    )

    print(f"\n  Training set: {len(X_train)} samples")
    print(f"  Validation set: {len(X_val)} samples")

    # Create model
    input_shape = (CONFIG['img_size'], CONFIG['img_size'], 3)
    model, base_model = create_model(len(class_names), input_shape)

    # Compile
    print("\n[3/6] Compiling model...")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=CONFIG['learning_rate']),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # Phase 1: Train only the top layers
    print("\n[4/6] Training Phase 1: Transfer Learning (frozen backbone)...")
    print(f"  Training for {CONFIG['epochs']} epochs...")

    history1 = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=CONFIG['epochs'],
        batch_size=CONFIG['batch_size'],
        callbacks=create_callbacks(CONFIG['model_name']),
        verbose=1
    )

    # Phase 2: Fine-tune the entire model
    print("\n[4/6] Training Phase 2: Fine-tuning (unfrozen backbone)...")

    # Unfreeze base model
    base_model.trainable = True
    print(f"  Unfreezing {len(base_model.layers)} layers in base model")

    # Recompile with lower learning rate
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=CONFIG['fine_tune_lr']),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    print(f"  Fine-tuning for {CONFIG['fine_tune_epochs']} epochs...")

    history2 = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=CONFIG['fine_tune_epochs'],
        batch_size=CONFIG['batch_size'],
        callbacks=create_callbacks(f"{CONFIG['model_name']}_finetuned"),
        verbose=1
    )

    # Combine histories
    history = history1
    for key in history1.history.keys():
        history.history[key].extend(history2.history[key])

    # Plot training history
    plot_training_history(history, CONFIG['model_name'])

    # Evaluate
    results = evaluate_model(model, X_val, y_val, class_names, CONFIG['model_name'])

    # Save final model
    print("\n  Saving models...")
    model.save(f'models/{CONFIG["model_name"]}_final.keras')
    print(f"  ✓ Saved: models/{CONFIG['model_name']}_final.keras")

    # Convert to TFLite
    tflite_path = convert_to_tflite(model, CONFIG['model_name'])

    # Save metadata
    metadata = {
        'model_name': CONFIG['model_name'],
        'timestamp': datetime.now().isoformat(),
        'class_names': class_names,
        'num_classes': len(class_names),
        'input_shape': list(input_shape),
        'accuracy': float(results['accuracy']),
        'config': CONFIG,
        'training_samples': len(X_train),
        'validation_samples': len(X_val)
    }

    with open(f'models/{CONFIG["model_name"]}_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    # Save class names
    with open(f'models/{CONFIG["model_name"]}_classes.pkl', 'wb') as f:
        pickle.dump(class_names, f)

    print(f"  ✓ Saved: models/{CONFIG['model_name']}_metadata.json")
    print(f"  ✓ Saved: models/{CONFIG['model_name']}_classes.pkl")

    # Summary
    print("\n" + "=" * 80)
    print("TRAINING COMPLETE!")
    print("=" * 80)
    print(f"\n✓ Final Validation Accuracy: {results['accuracy']*100:.2f}%")
    print(f"✓ Mean Confidence: {np.mean(results['confidences'])*100:.1f}%")
    print(f"\nFiles saved:")
    print(f"  - models/{CONFIG['model_name']}_best.keras (best checkpoint)")
    print(f"  - models/{CONFIG['model_name']}_final.keras (final model)")
    print(f"  - models/{CONFIG['model_name']}.tflite (Pi deployment)")
    print(f"  - models/{CONFIG['model_name']}_metadata.json")
    print(f"  - models/{CONFIG['model_name']}_classes.pkl")
    print(f"  - models/{CONFIG['model_name']}_training_history.png")
    print(f"  - models/{CONFIG['model_name']}_confusion_matrix.png")
    print(f"  - models/{CONFIG['model_name']}_classification_report.txt")

    print("\n" + "=" * 80)
    print("Next steps:")
    print("  1. Review training plots and confusion matrix")
    print("  2. Update config/config.yaml to use new model")
    print("  3. Test with: python test_with_real_images.py")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
