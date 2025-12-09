"""
Config loader for the plankton analysis system
"""

import yaml
from pathlib import Path


def load_config(config_path='config/config.yaml'):
    """Load configuration from YAML file"""
    config_file = Path(config_path)

    if not config_file.exists():
        # Return default config
        return {
            'classification': {
                'model_path': 'models/best_model_checkpoint.keras',
                'confidence_threshold': 0.3
            }
        }

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return config
