#!/usr/bin/env python3
"""
Comprehensive Model Evaluation Script
Generates detailed performance metrics, confusion matrix, and per-class analysis
"""

import os
import sys
import numpy as np
import cv2
import tensorflow as tf
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
    precision_recall_fscore_support
)
from collections import Counter
import json


def load_model_and_metadata():
    """Load the best trained model and its metadata"""
    model_path = 'models/best_model_checkpoint.keras'
    metadata_path = 'models/model_metadata.pkl'

    if not os.path.exists(model_path):
        print(f"❌ Model not found at {model_path}")
        sys.exit(1)

    print(f"Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path)

    # Load metadata
    if os.path.exists(metadata_path):
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        class_names = metadata.get('class_names', [])
        input_size = 224  # EfficientNetB0 uses 224x224
    else:
        print(f"❌ Metadata not found at {metadata_path}")
        sys.exit(1)

    print(f"✅ Model loaded successfully")
    print(f"   Classes: {len(class_names)}")
    print(f"   Input size: {input_size}x{input_size}\n")

    return model, class_names, input_size


def load_validation_data(data_dir='datasets/raw/dataset_pm/training', input_size=224):
    """Load validation dataset (same split as training)"""
    print("Loading validation dataset...")

    if not os.path.exists(data_dir):
        print(f"❌ Dataset directory not found: {data_dir}")
        return None, None, None

    # Load ALL images first (same as training)
    from sklearn.model_selection import train_test_split

    images = []
    labels = []
    class_names = []

    # Get all class directories
    class_dirs = sorted([Path(data_dir) / d for d in os.listdir(data_dir)
                        if (Path(data_dir) / d).is_dir() and d != 'desktop.ini'])

    if not class_dirs:
        print(f"❌ No class directories found in {data_dir}")
        return None, None, None

    print(f"Found {len(class_dirs)} classes")

    # Load all images
    for class_idx, class_dir in enumerate(class_dirs):
        class_name = class_dir.name
        class_names.append(class_name)

        # Load all .png files (same as training)
        image_files = list(class_dir.glob('*.png'))

        print(f"  Loading class '{class_name}': {len(image_files)} images")

        for img_file in image_files:
            img = cv2.imread(str(img_file))

            if img is not None:
                # Preprocess (same as training)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (input_size, input_size))
                img = img.astype('float32') / 255.0

                images.append(img)
                labels.append(class_idx)

    images = np.array(images)
    labels = np.array(labels)

    # Split same way as training (80/20, same random_state)
    _, X_val, _, y_val = train_test_split(
        images, labels, test_size=0.2, random_state=42, stratify=labels
    )

    print(f"✅ Loaded {len(X_val)} validation images (20% split)")
    print(f"   Classes: {len(class_names)}")
    print(f"   Distribution: {dict(Counter(y_val))}\n")

    return X_val, y_val, class_names


def evaluate_model(model, images, labels, class_names):
    """Evaluate model on validation set"""
    print("Evaluating model...")

    # Get predictions
    predictions = model.predict(images, verbose=1)
    predicted_classes = np.argmax(predictions, axis=1)

    # Calculate metrics
    accuracy = accuracy_score(labels, predicted_classes)

    # Per-class metrics
    precision, recall, f1, support = precision_recall_fscore_support(
        labels, predicted_classes, average=None, zero_division=0
    )

    # Confusion matrix
    cm = confusion_matrix(labels, predicted_classes)

    # Overall metrics
    precision_avg, recall_avg, f1_avg, _ = precision_recall_fscore_support(
        labels, predicted_classes, average='weighted', zero_division=0
    )

    print(f"\n{'='*80}")
    print(f"OVERALL PERFORMANCE")
    print(f"{'='*80}")
    print(f"Overall Accuracy:  {accuracy*100:.2f}%")
    print(f"Precision (avg):   {precision_avg*100:.2f}%")
    print(f"Recall (avg):      {recall_avg*100:.2f}%")
    print(f"F1-Score (avg):    {f1_avg*100:.2f}%")
    print(f"{'='*80}\n")

    return {
        'accuracy': accuracy,
        'predictions': predictions,
        'predicted_classes': predicted_classes,
        'confusion_matrix': cm,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'support': support,
        'precision_avg': precision_avg,
        'recall_avg': recall_avg,
        'f1_avg': f1_avg
    }


def print_per_class_report(class_names, precision, recall, f1, support):
    """Print detailed per-class performance"""
    print(f"\n{'='*80}")
    print(f"PER-CLASS PERFORMANCE")
    print(f"{'='*80}")
    print(f"{'Class':<30} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'Support':>10}")
    print(f"{'-'*80}")

    for i, class_name in enumerate(class_names):
        print(f"{class_name:<30} {precision[i]*100:>9.1f}% {recall[i]*100:>9.1f}% "
              f"{f1[i]*100:>9.1f}% {support[i]:>10}")

    print(f"{'='*80}\n")


def plot_confusion_matrix(cm, class_names, output_path='results/confusion_matrix.png'):
    """Plot confusion matrix"""
    print("Generating confusion matrix plot...")

    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Plot
    plt.figure(figsize=(16, 14))

    # Normalize confusion matrix
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    # Plot
    sns.heatmap(cm_normalized, annot=True, fmt='.2f', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names,
                cbar_kws={'label': 'Proportion'})

    plt.title('Confusion Matrix (Normalized)\nBest Model: EfficientNetB0 Transfer Learning',
              fontsize=14, pad=20)
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ Saved confusion matrix to {output_path}")
    plt.close()


def plot_per_class_metrics(class_names, precision, recall, f1,
                           output_path='results/per_class_metrics.png'):
    """Plot per-class performance metrics"""
    print("Generating per-class metrics plot...")

    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Prepare data
    x = np.arange(len(class_names))
    width = 0.25

    fig, ax = plt.subplots(figsize=(16, 8))

    # Plot bars
    rects1 = ax.bar(x - width, precision * 100, width, label='Precision', alpha=0.8)
    rects2 = ax.bar(x, recall * 100, width, label='Recall', alpha=0.8)
    rects3 = ax.bar(x + width, f1 * 100, width, label='F1-Score', alpha=0.8)

    # Formatting
    ax.set_ylabel('Score (%)', fontsize=12)
    ax.set_title('Per-Class Performance Metrics\nBest Model: EfficientNetB0 Transfer Learning',
                 fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(class_names, rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 100)

    # Add value labels on bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 5:  # Only label if bar is tall enough
                ax.annotate(f'{height:.0f}',
                          xy=(rect.get_x() + rect.get_width() / 2, height),
                          xytext=(0, 3),
                          textcoords="offset points",
                          ha='center', va='bottom', fontsize=7)

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ Saved per-class metrics to {output_path}")
    plt.close()


def plot_class_distribution(labels, class_names,
                            output_path='results/class_distribution.png'):
    """Plot class distribution in validation set"""
    print("Generating class distribution plot...")

    # Count samples per class
    counts = Counter(labels)

    fig, ax = plt.subplots(figsize=(16, 6))

    x = np.arange(len(class_names))
    heights = [counts.get(i, 0) for i in range(len(class_names))]

    bars = ax.bar(x, heights, alpha=0.8, color='steelblue')

    # Formatting
    ax.set_ylabel('Number of Samples', fontsize=12)
    ax.set_title('Validation Set Class Distribution', fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(class_names, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ Saved class distribution to {output_path}")
    plt.close()


def save_evaluation_report(results, class_names, output_path='results/evaluation_report.json'):
    """Save evaluation results to JSON"""
    print("Saving evaluation report...")

    report = {
        'overall_metrics': {
            'accuracy': float(results['accuracy']),
            'precision_avg': float(results['precision_avg']),
            'recall_avg': float(results['recall_avg']),
            'f1_avg': float(results['f1_avg'])
        },
        'per_class_metrics': []
    }

    for i, class_name in enumerate(class_names):
        report['per_class_metrics'].append({
            'class_name': class_name,
            'precision': float(results['precision'][i]),
            'recall': float(results['recall'][i]),
            'f1_score': float(results['f1'][i]),
            'support': int(results['support'][i])
        })

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✅ Saved evaluation report to {output_path}\n")


def main():
    print("="*80)
    print("COMPREHENSIVE MODEL EVALUATION")
    print("="*80)
    print()

    # Load model
    model, class_names, input_size = load_model_and_metadata()

    # Load validation data
    images, labels, data_class_names = load_validation_data(input_size=input_size)

    if images is None:
        print("❌ Failed to load validation data")
        sys.exit(1)

    # Ensure class names match
    if data_class_names != class_names:
        print("⚠️  Warning: Class names from data don't match model metadata")
        print(f"   Using model class names: {class_names}")

    # Evaluate
    results = evaluate_model(model, images, labels, class_names)

    # Print per-class report
    print_per_class_report(
        class_names,
        results['precision'],
        results['recall'],
        results['f1'],
        results['support']
    )

    # Generate visualizations
    plot_confusion_matrix(results['confusion_matrix'], class_names)
    plot_per_class_metrics(class_names, results['precision'],
                           results['recall'], results['f1'])
    plot_class_distribution(labels, class_names)

    # Save report
    save_evaluation_report(results, class_names)

    print("="*80)
    print("✅ EVALUATION COMPLETE")
    print("="*80)
    print("\nGenerated files:")
    print("  - results/confusion_matrix.png")
    print("  - results/per_class_metrics.png")
    print("  - results/class_distribution.png")
    print("  - results/evaluation_report.json")
    print()


if __name__ == '__main__':
    main()
