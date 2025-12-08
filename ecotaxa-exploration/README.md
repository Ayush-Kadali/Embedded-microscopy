# EcoTaxa Exploration & Integration

This directory contains everything related to exploring EcoTaxa platform, testing its capabilities, and integrating it into our plankton classification prototype.

## 📁 Directory Structure

```
ecotaxa-exploration/
├── docs/               # Documentation and research notes
├── scripts/            # Python scripts for EcoTaxa API interaction
├── test_images/        # Sample plankton images for testing
├── results/            # Classification results from EcoTaxa
├── notebooks/          # Jupyter notebooks for experimentation
└── README.md           # This file
```

## 🎯 Goals

1. **Understand EcoTaxa Workflow**: Learn how EcoTaxa analyzes and classifies plankton images
2. **Test Classification Accuracy**: Upload sample images and evaluate results
3. **API Integration**: Explore programmatic access via Python API
4. **Prototype Integration**: Determine if/how to integrate EcoTaxa into our first prototype

## 📚 What is EcoTaxa?

**EcoTaxa** is a collaborative web platform for taxonomic classification of plankton and other marine organism images.

### Key Features:
- **650+ million images** from 850+ institutions and 4000+ users
- **Machine Learning Assisted Classification**: Supervised ML predictions help speed up annotation
- **Visual Similarity Search**: Find similar organisms in the database
- **Multiple Imaging Instruments**: Supports ZooScan, UVP, FlowCAM, IFCB, and more
- **Data Export**: Export in DarwinCore, OBIS, GBIF formats
- **API Access**: Full REST API with Python and R clients
- **Free for Scientific Use**: Open platform for research

## 🔑 Key Capabilities

### 1. Image Upload & Management
- Upload individual or batch plankton images
- Organize images into projects
- Add metadata (location, depth, date, equipment)

### 2. Classification
- **Manual Classification**: Human experts annotate images
- **ML-Assisted Classification**: Trained models suggest classifications
- **Visual Similarity**: Find similar organisms to aid identification

### 3. Data Export
- CSV/TSV export with taxonomic data
- DarwinCore format for biodiversity databases
- JSON/XML via API

### 4. Collaboration
- Multi-user projects
- Role-based access (viewer, annotator, manager)
- Public and private datasets

## 🔧 Technical Architecture

### API Endpoint
- **Base URL**: `https://ecotaxa.obs-vlfr.fr/api`
- **Documentation**: https://ecotaxa.obs-vlfr.fr/api/docs
- **API Version**: 0.0.37

### Available APIs

#### Core APIs:
- **AuthenticationApi**: Login and access token management
- **ProjectsApi**: Create, manage, merge, subset projects
- **ObjectsApi**: Query, classify, export object data
- **SamplesApi**: Sample metadata management
- **TaxonomyApi**: Taxonomic tree and classification
- **JobsApi**: Manage long-running jobs
- **FilesApi**: Upload and manage files

#### Data Flow:
```
Upload Images → Create Project → Add Metadata →
ML Prediction → Manual Review → Export Results
```

## 📦 Installation

### Python Client

```bash
# Install from GitHub
pip install git+https://github.com/ecotaxa/ecotaxa_py_client.git

# Or clone and install locally
git clone https://github.com/ecotaxa/ecotaxa_py_client.git
cd ecotaxa_py_client
pip install -e .
```

### Additional Tools

```bash
# For data processing
pip install pandas numpy

# For image handling
pip install pillow opencv-python

# For Jupyter notebooks
pip install jupyter notebook
```

## 🚀 Quick Start Guide

### 1. Create Account
1. Go to https://ecotaxa.obs-vlfr.fr/
2. Click "Sign Up" (or request account if needed)
3. Verify email and log in

### 2. Test with Web Interface
1. Create a new project
2. Upload a few test plankton images
3. Add metadata (sampling info, location)
4. Use ML prediction to get suggested classifications
5. Review and validate predictions
6. Export results as CSV

### 3. Test with Python API
See `scripts/01_basic_authentication.py` for authentication example
See `scripts/02_create_project.py` for project creation
See `scripts/03_upload_images.py` for image upload

## 🔬 How EcoTaxa Analyzes Images

### Analysis Pipeline:

1. **Image Upload**
   - Images uploaded with metadata
   - Automatic thumbnail generation
   - Feature extraction (optional)

2. **ML Prediction**
   - Pre-trained CNN models for common taxa
   - Confidence scores for each prediction
   - Top-N predictions per image

3. **Visual Similarity**
   - Deep learning embeddings
   - Find visually similar organisms
   - Cross-reference with validated data

4. **Human Validation**
   - Expert review of predictions
   - Consensus building for difficult cases
   - Continuous model improvement

5. **Export & Analysis**
   - Validated classifications exported
   - Biodiversity metrics calculated
   - Integration with other tools

### ML Models Used:
- **CNN Architectures**: ResNet, EfficientNet variants
- **Training Data**: 650+ million validated images
- **Classes**: Thousands of species across multiple taxa
- **Accuracy**: Varies by taxa, typically 80-95% for common species

## 📊 Integration Options for Our Prototype

### Option 1: Web Upload (Manual) ⭐ EASIEST
**Use Case**: Testing, validation, small batches

**Pros**:
- No coding required
- Access to full platform features
- High-quality ML models
- Expert community support

**Cons**:
- Manual process
- Not automated
- Requires internet connection
- Not suitable for real-time field use

**Implementation**:
1. Capture images with our system
2. Upload to EcoTaxa via web interface
3. Get classifications
4. Download results
5. Compare with our model

### Option 2: API Integration (Automated) ⭐⭐ MODERATE
**Use Case**: Batch processing, validation, cloud backup

**Pros**:
- Fully automated
- Programmatic access
- Can be scheduled
- Access to expert classifications

**Cons**:
- Requires internet connection
- API rate limits
- More complex implementation
- Depends on external service

**Implementation**:
```python
# Pseudo-code
from ecotaxa_client import ApiClient, ProjectsApi, ObjectsApi

# 1. Authenticate
client = authenticate(username, password)

# 2. Create project
project_id = create_project(client, "RaspberryPi_Field_Samples")

# 3. Upload images from Raspberry Pi
for image in captured_images:
    upload_image(client, project_id, image, metadata)

# 4. Trigger ML prediction
predict_classifications(client, project_id)

# 5. Retrieve results
results = get_classifications(client, project_id)

# 6. Compare with our model
compare_results(our_predictions, ecotaxa_results)
```

### Option 3: Hybrid Approach ⭐⭐⭐ RECOMMENDED
**Use Case**: Development, validation, gradual deployment

**Pros**:
- Best of both worlds
- Use EcoTaxa for training data
- Use local model for field deployment
- EcoTaxa for validation and improvement

**Cons**:
- More complex system
- Requires both local and cloud components

**Implementation**:
1. **Development Phase**:
   - Use EcoTaxa to label training data
   - Export labeled dataset
   - Train our own model using EcoTaxa labels

2. **Deployment Phase**:
   - Run our model locally on Raspberry Pi
   - Store predictions locally

3. **Validation Phase**:
   - Periodically upload samples to EcoTaxa
   - Compare predictions
   - Retrain model with new data

### Option 4: Download Pretrained Model ⭐⭐⭐⭐ BEST FOR PROTOTYPE
**Use Case**: Fast prototyping, offline deployment

**Pros**:
- Works offline
- Fast inference on Pi
- No API dependencies
- Full control

**Cons**:
- May not have access to EcoTaxa's exact models
- Need to find compatible model architecture
- May need to retrain for our specific use case

**Implementation**:
1. Contact EcoTaxa team for model weights (if available)
2. Or use similar architecture (ResNet, EfficientNet)
3. Fine-tune on plankton dataset from EcoTaxa exports
4. Deploy to Raspberry Pi as TFLite

## 🎯 Recommended Strategy for Prototype

### Phase 1: Testing & Validation (Week 1)
- [ ] Create EcoTaxa account
- [ ] Upload 50-100 test images via web interface
- [ ] Analyze classification results
- [ ] Compare accuracy with known species
- [ ] Document workflow and results

### Phase 2: API Experimentation (Week 1-2)
- [ ] Install Python client
- [ ] Write authentication script
- [ ] Create test project via API
- [ ] Upload images programmatically
- [ ] Retrieve and analyze results
- [ ] Measure API latency and limits

### Phase 3: Dataset Building (Week 2)
- [ ] Export validated datasets from EcoTaxa
- [ ] Download training images
- [ ] Create our own labeled dataset
- [ ] Prepare data for model training

### Phase 4: Model Training (Week 2-3)
- [ ] Train custom model on EcoTaxa-derived dataset
- [ ] Convert to TFLite for Raspberry Pi
- [ ] Benchmark accuracy against EcoTaxa predictions
- [ ] Optimize for edge deployment

### Phase 5: Prototype Integration (Week 3)
- [ ] Decision: Use EcoTaxa API or local model?
- [ ] If API: Implement upload/retrieve workflow
- [ ] If local: Deploy trained model to Pi
- [ ] If hybrid: Implement both with fallback logic

### Phase 6: Demo Preparation (Week 4)
- [ ] Test end-to-end workflow
- [ ] Prepare comparison: Our model vs EcoTaxa
- [ ] Document accuracy metrics
- [ ] Create demo slides showing EcoTaxa validation

## 📝 Next Steps

1. **Read**: `docs/ECOTAXA_WORKFLOW.md` - Detailed workflow guide
2. **Run**: `scripts/01_basic_authentication.py` - Test API access
3. **Explore**: `notebooks/01_ecotaxa_exploration.ipynb` - Interactive testing
4. **Test**: Upload images via web interface to understand the process

## 🔗 Useful Links

- **EcoTaxa Platform**: https://ecotaxa.obs-vlfr.fr/
- **API Documentation**: https://ecotaxa.obs-vlfr.fr/api/docs
- **Python Client GitHub**: https://github.com/ecotaxa/ecotaxa_py_client
- **EcoTaxa GitHub Organization**: https://github.com/ecotaxa
- **JERICO-RI EcoTaxa Info**: https://www.jerico-ri.eu/va-service/ecotaxa/

## 📧 Support

- **EcoTaxa Support**: Contact via platform
- **GitHub Issues**: https://github.com/ecotaxa/ecotaxa_py_client/issues
- **Community**: 4000+ users on the platform

---

**Status**: Exploration phase - actively testing and documenting capabilities

**Last Updated**: 2025-12-08
