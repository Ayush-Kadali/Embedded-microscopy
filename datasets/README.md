# Datasets Directory

## Structure

```
datasets/
├── raw/              # Original downloaded images (not in git)
├── processed/        # Preprocessed images (not in git)
├── metadata.csv      # Image information (tracked in git)
└── README.md         # This file
```

## Notes

- Image files are too large for Git and are in .gitignore
- Share images via Google Drive or team shared folder
- Each team member should download separately

## Setup

```bash
# Create directories (already created if you see this)
mkdir -p datasets/raw datasets/processed

# Download images
# (Instructions will be provided by Person 3 - Data Collection lead)
```

## For Person 3 (Data Collection Lead)

See `docs/MODULE_DEVELOPMENT.md` section "Person 3: Data Collection Module" for:
- How to download datasets from Kaggle
- Image preprocessing instructions
- How to organize the dataset
- How to integrate with acquisition module

## For Other Team Members

If you need test images:
1. Ask Person 3 for shared folder link
2. Download to `datasets/processed/`
3. Images will automatically be used by pipeline
