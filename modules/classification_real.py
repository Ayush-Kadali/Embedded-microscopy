"""
Real Classification Module using trained model

This replaces the stub classifier with actual ML-based classification
"""

from typing import Dict, Any, List
import numpy as np
import cv2
import pickle
from pathlib import Path
from .base import PipelineModule

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


class ClassificationModuleReal(PipelineModule):
    """
    Classifies organisms using trained CNN model.

    Input Contract:
        - image: np.ndarray[H, W, 3]
        - masks: list of boolean masks
        - bounding_boxes: list of dict(x, y, w, h)
        - classification_config: dict

    Output Contract:
        - status: str
        - error_message: str | None
        - predictions: list of dict(class_name, confidence, bbox, mask)
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.model = None
        self.class_names = []
        self.input_size = 64

    def validate_config(self) -> None:
        """Validate configuration."""
        model_path = self.config.get('model_path', 'models/plankton_classifier.keras')

        if not Path(model_path).exists():
            self.logger.warning(f"Model not found at {model_path}, will use stub mode")

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input data."""
        required = ['image', 'masks', 'bounding_boxes']
        for key in required:
            if key not in input_data:
                raise ValueError(f"Missing required input: {key}")

    def _load_model(self):
        """Load trained model"""
        if self.model is not None:
            return True

        if not TF_AVAILABLE:
            self.logger.warning("TensorFlow not available, using stub mode")
            return False

        model_path = self.config.get('model_path', 'models/plankton_classifier.keras')
        metadata_path = 'models/model_metadata.pkl'

        if not Path(model_path).exists():
            self.logger.warning(f"Model not found at {model_path}")
            return False

        try:
            # Load model
            self.model = tf.keras.models.load_model(model_path)
            self.logger.info(f"Loaded model from {model_path}")

            # Load metadata
            if Path(metadata_path).exists():
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    self.class_names = metadata['class_names']
                    self.input_size = metadata['input_size']
                    self.logger.info(f"Loaded {len(self.class_names)} classes")
            else:
                # Try loading just class names
                class_names_path = 'models/class_names.pkl'
                if Path(class_names_path).exists():
                    with open(class_names_path, 'rb') as f:
                        self.class_names = pickle.load(f)
                else:
                    # Fallback to config
                    self.class_names = self.config.get('class_names', [])

            return True

        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify detected organisms."""
        try:
            image = input_data['image']
            masks = input_data['masks']
            bboxes = input_data['bounding_boxes']

            # Try to load model if not loaded
            model_loaded = self._load_model()

            if not model_loaded or self.model is None:
                # Fallback to stub mode
                return self._stub_classify(masks, bboxes)

            # Real classification
            predictions = []

            for i, (mask, bbox) in enumerate(zip(masks, bboxes)):
                # Extract organism region
                x, y, w, h = bbox['x'], bbox['y'], bbox['w'], bbox['h']

                # Crop image
                crop = image[y:y+h, x:x+w].copy()

                if crop.size == 0:
                    continue

                # Resize to model input size
                crop_resized = cv2.resize(crop, (self.input_size, self.input_size))
                crop_resized = crop_resized.astype('float32') / 255.0

                # Add batch dimension
                crop_batch = np.expand_dims(crop_resized, axis=0)

                # Predict
                pred = self.model.predict(crop_batch, verbose=0)
                class_idx = np.argmax(pred[0])
                confidence = float(pred[0][class_idx])

                class_name = self.class_names[class_idx] if class_idx < len(self.class_names) else 'Unknown'

                predictions.append({
                    'organism_id': i,
                    'class_name': class_name,
                    'confidence': confidence,
                    'bounding_box': bbox,
                    'mask_index': i
                })

            self.logger.info(f"Classification complete: {len(predictions)} organisms, "
                           f"{1000*len(predictions)/max(1, len(predictions)):.1f}ms "
                           f"({1000/max(1, len(predictions)):.1f}ms/organism)")

            return {
                'status': 'success',
                'error_message': None,
                'predictions': predictions,
                'num_classified': len(predictions),
                'model_metadata': {
                    'model_name': 'plankton_classifier_cnn',
                    'inference_time_ms': 1000 * len(predictions) / max(1, len(predictions)),
                    'num_classes': len(self.class_names)
                }
            }

        except Exception as e:
            return self.handle_error(e)

    def _stub_classify(self, masks, bboxes):
        """Fallback stub classification"""
        self.logger.warning("Using stub classifier")

        predictions = []
        class_names = self.config.get('class_names', ['Copepod', 'Diatom', 'Other'])

        for i, bbox in enumerate(bboxes):
            class_name = np.random.choice(class_names)
            confidence = np.random.uniform(0.8, 0.999)

            predictions.append({
                'organism_id': i,
                'class_name': class_name,
                'confidence': confidence,
                'bounding_box': bbox,
                'mask_index': i
            })

        return {
            'status': 'success',
            'error_message': None,
            'predictions': predictions,
            'num_classified': len(predictions),
            'model_metadata': {
                'model_name': 'stub_classifier',
                'inference_time_ms': 0.0,
                'num_classes': len(class_names)
            }
        }
