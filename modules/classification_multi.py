"""
Multi-Model Classification Module

Supports:
1. Model 1: Original lightweight classifier
2. Model 2: MobileNetV2 transfer learning model
3. Ensemble: Both models voting together

Usage in config.yaml:
  classification:
    mode: 'model_1'  # or 'model_2' or 'ensemble'
    model_1_path: 'models/plankton_classifier.keras'
    model_2_path: 'models/plankton_mobilenet_v2_best.keras'
    confidence_threshold: 0.3
"""

import numpy as np
import cv2
from pathlib import Path
import pickle
import json
from modules.base import PipelineModule

class ClassificationMultiModel(PipelineModule):
    """
    Multi-model classification with switching and ensemble support
    """

    def __init__(self, config):
        # Set attributes BEFORE calling super().__init__()
        # because super() calls validate_config() which needs these attributes
        self.mode = config.get('mode', 'model_1')  # model_1, model_2, or ensemble
        self.confidence_threshold = config.get('confidence_threshold', 0.3)

        # Model paths
        self.model_1_path = config.get('model_1_path', 'models/plankton_classifier.keras')
        self.model_2_path = config.get('model_2_path', 'models/plankton_mobilenet_v2_best.keras')

        # Ensemble weights (how much to trust each model)
        self.ensemble_weights = config.get('ensemble_weights', [0.5, 0.5])  # [model_1, model_2]

        # Initialize models based on mode
        self.model_1 = None
        self.model_2 = None
        self.class_names = None

        # Now call parent init (which calls validate_config)
        super().__init__(config)

        # Load models after validation
        self._load_models()

    def _load_models(self):
        """Load models based on selected mode"""
        import tensorflow as tf

        self.logger.info(f"Classification mode: {self.mode}")

        # Load class names (same for both models)
        class_names_path = Path('models/class_names.pkl')
        if class_names_path.exists():
            with open(class_names_path, 'rb') as f:
                self.class_names = pickle.load(f)
        else:
            # Default class names
            self.class_names = [
                'Alexandrium', 'Asterionellopsis glacialis', 'Cerataulina', 'Ceratium',
                'Chaetoceros', 'Entomoneis', 'Guinardia', 'Hemiaulus',
                'Lauderia annulata', 'Nitzschia', 'Noctiluca', 'Ornithocercus magnificus',
                'Pinnularia', 'Pleurosigma', 'Prorocentrum', 'Protoperidinium',
                'Pyrodinium', 'Thalassionema', 'Thalassiosira'
            ]

        # Load Model 1 (EfficientNetB0) if needed
        if self.mode in ['model_1', 'ensemble']:
            if Path(self.model_1_path).exists():
                self.logger.info(f"Loading Model 1: {self.model_1_path}")
                self.model_1 = tf.keras.models.load_model(self.model_1_path)
                self.logger.info(f"  ✓ Model 1 loaded (EfficientNetB0, input: 224x224)")
            else:
                self.logger.warning(f"Model 1 not found: {self.model_1_path}")
                if self.mode == 'model_1':
                    raise FileNotFoundError(f"Model 1 required but not found: {self.model_1_path}")

        # Load Model 2 (MobileNetV2) if needed
        if self.mode in ['model_2', 'ensemble']:
            if Path(self.model_2_path).exists():
                self.logger.info(f"Loading Model 2: {self.model_2_path}")
                self.model_2 = tf.keras.models.load_model(self.model_2_path)
                self.logger.info(f"  ✓ Model 2 loaded (MobileNetV2, input: 128x128)")
            else:
                self.logger.warning(f"Model 2 not found: {self.model_2_path}")
                if self.mode == 'model_2':
                    raise FileNotFoundError(f"Model 2 required but not found: {self.model_2_path}")

        self.logger.info(f"Loaded {len(self.class_names)} classes")

    def validate_config(self):
        """Validate configuration"""
        if self.mode not in ['model_1', 'model_2', 'ensemble']:
            return False, f"Invalid mode: {self.mode}. Must be 'model_1', 'model_2', or 'ensemble'"

        if self.mode == 'ensemble' and len(self.ensemble_weights) != 2:
            return False, "Ensemble mode requires exactly 2 weights"

        if abs(sum(self.ensemble_weights) - 1.0) > 0.01:
            return False, f"Ensemble weights must sum to 1.0, got {sum(self.ensemble_weights)}"

        return True, ""

    def validate_input(self, input_data):
        """Validate input data"""
        required_keys = ['preprocessed_image', 'mask', 'labeled_mask', 'organisms']

        for key in required_keys:
            if key not in input_data:
                return False, f"Missing required key: {key}"

        if input_data['preprocessed_image'] is None:
            return False, "preprocessed_image is None"

        if len(input_data['organisms']) == 0:
            return False, "No organisms to classify"

        return True, ""

    def _extract_organism_crop(self, image, bbox, target_size):
        """Extract and preprocess organism crop"""
        x, y, w, h = bbox

        # Extract crop with bounds checking
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(image.shape[1], x + w)
        y2 = min(image.shape[0], y + h)

        crop = image[y1:y2, x1:x2]

        if crop.size == 0:
            # Return blank image if crop is invalid
            return np.zeros((target_size, target_size, 3), dtype=np.float32)

        # Resize to target size
        crop_resized = cv2.resize(crop, (target_size, target_size))

        # Normalize to [0, 1]
        crop_normalized = crop_resized.astype(np.float32) / 255.0

        return crop_normalized

    def _classify_with_model_1(self, organism_crops):
        """Classify with Model 1 (224x224 input - EfficientNetB0)"""
        if self.model_1 is None:
            return None

        # Prepare crops for Model 1 (224x224)
        crops_224 = np.array([self._extract_organism_crop(
            crop * 255, (0, 0, crop.shape[1], crop.shape[0]), 224
        ) for crop in organism_crops])

        # Predict
        predictions = self.model_1.predict(crops_224, verbose=0)

        return predictions

    def _classify_with_model_2(self, organism_crops):
        """Classify with Model 2 (128x128 input - MobileNetV2)"""
        if self.model_2 is None:
            return None

        # Prepare crops for Model 2 (128x128)
        crops_128 = np.array([self._extract_organism_crop(
            crop * 255, (0, 0, crop.shape[1], crop.shape[0]), 128
        ) for crop in organism_crops])

        # MobileNetV2 preprocessing
        import tensorflow as tf
        crops_preprocessed = tf.keras.applications.mobilenet_v2.preprocess_input(crops_128 * 255)

        # Predict
        predictions = self.model_2.predict(crops_preprocessed, verbose=0)

        return predictions

    def _ensemble_predictions(self, pred_1, pred_2):
        """Combine predictions from both models"""
        # Weighted average
        ensemble_pred = (
            self.ensemble_weights[0] * pred_1 +
            self.ensemble_weights[1] * pred_2
        )

        return ensemble_pred

    def process(self, input_data):
        """Process organisms and classify them"""
        try:
            image = input_data['preprocessed_image']
            organisms = input_data['organisms']

            # Extract crops for all organisms
            organism_crops = []
            for org in organisms:
                bbox = org['bbox']
                crop = image[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]]
                organism_crops.append(crop / 255.0 if crop.max() > 1 else crop)

            # Get predictions based on mode
            if self.mode == 'model_1':
                predictions = self._classify_with_model_1(organism_crops)
                model_info = {'active_models': ['model_1'], 'mode': 'single'}

            elif self.mode == 'model_2':
                predictions = self._classify_with_model_2(organism_crops)
                model_info = {'active_models': ['model_2'], 'mode': 'single'}

            elif self.mode == 'ensemble':
                pred_1 = self._classify_with_model_1(organism_crops)
                pred_2 = self._classify_with_model_2(organism_crops)

                if pred_1 is not None and pred_2 is not None:
                    predictions = self._ensemble_predictions(pred_1, pred_2)
                    model_info = {
                        'active_models': ['model_1', 'model_2'],
                        'mode': 'ensemble',
                        'weights': self.ensemble_weights,
                        'individual_predictions': {
                            'model_1': pred_1.tolist(),
                            'model_2': pred_2.tolist()
                        }
                    }
                elif pred_1 is not None:
                    predictions = pred_1
                    model_info = {'active_models': ['model_1'], 'mode': 'fallback'}
                elif pred_2 is not None:
                    predictions = pred_2
                    model_info = {'active_models': ['model_2'], 'mode': 'fallback'}
                else:
                    raise RuntimeError("No models available for ensemble")

            # Process predictions
            classified_organisms = []

            for i, org in enumerate(organisms):
                pred = predictions[i]
                class_idx = np.argmax(pred)
                confidence = float(pred[class_idx])

                # Get top-k predictions
                top_k_indices = np.argsort(pred)[::-1][:3]
                top_k_predictions = [
                    {
                        'class_name': self.class_names[idx],
                        'confidence': float(pred[idx])
                    }
                    for idx in top_k_indices
                ]

                classified_organisms.append({
                    **org,  # Include all original organism data
                    'class_name': self.class_names[class_idx],
                    'class_idx': int(class_idx),
                    'confidence': confidence,
                    'top_k_predictions': top_k_predictions,
                    'passes_threshold': confidence >= self.confidence_threshold
                })

            return {
                'status': 'success',
                'organisms': classified_organisms,
                'num_organisms': len(classified_organisms),
                'num_above_threshold': sum(1 for org in classified_organisms if org['passes_threshold']),
                'model_metadata': model_info,
                'class_names': self.class_names
            }

        except Exception as e:
            self.logger.error(f"Classification failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'organisms': []
            }
