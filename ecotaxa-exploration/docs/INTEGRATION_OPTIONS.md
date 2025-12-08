# EcoTaxa Integration Options for Prototype

This document analyzes different ways to integrate EcoTaxa into our Marine Plankton AI Microscopy System prototype.

---

## 🎯 Integration Goals

1. **Validate our model** against EcoTaxa's established classifications
2. **Leverage existing expertise** from 650M+ classified images
3. **Improve accuracy** through comparison and learning
4. **Build credibility** by showing alignment with recognized platform
5. **Access training data** for model improvement

---

## 📊 Integration Options Comparison

| Option | Complexity | Offline Capable | API Dependency | Best For | Time to Implement |
|--------|-----------|----------------|----------------|----------|-------------------|
| 1. Manual Web Upload | ⭐ Low | ❌ No | ❌ No | Testing, Validation | 1 hour |
| 2. API Integration | ⭐⭐⭐ High | ❌ No | ✅ Yes | Automated Validation | 2-3 days |
| 3. Download Dataset | ⭐⭐ Medium | ✅ Yes | ❌ No | Model Training | 1-2 days |
| 4. Hybrid Approach | ⭐⭐⭐⭐ Very High | ✅ Partial | ⚠️ Optional | Production System | 1 week |
| 5. Reference Only | ⭐ Very Low | ✅ Yes | ❌ No | Demo/Presentation | 1 hour |

---

## Option 1: Manual Web Upload (Validation Only)

### Overview
Upload sample images through EcoTaxa web interface to validate our classification results.

### Implementation Steps

1. **Capture images with our system** (Raspberry Pi + HQ Camera)
2. **Run our classification model** locally
3. **Upload same images to EcoTaxa** via web interface
4. **Compare results**
5. **Document differences** in presentation

### Workflow Diagram
```
[Our System] → Capture → Classify Locally → Save Results
                            ↓
                    Upload to EcoTaxa
                            ↓
                    Manual Classification
                            ↓
                    Compare Results
                            ↓
              Show Accuracy in Demo
```

### Pros
- ✅ **Simple** - no coding required
- ✅ **Quick** - can be done in hours
- ✅ **Credible** - shows comparison with established platform
- ✅ **No dependencies** - doesn't affect system reliability

### Cons
- ❌ **Manual process** - not automated
- ❌ **Slow** - can't process many samples
- ❌ **Not real-time** - requires internet and time
- ❌ **Limited scope** - only for demo purposes

### Recommended For
- **Hackathon demo**: Show that we validated against EcoTaxa
- **Quick testing**: Test 10-20 samples
- **Credibility**: "Our model matches EcoTaxa 85% accuracy"

### Integration Code
Not required - manual process only.

### Time Estimate
- Setup: 30 minutes (create account, test upload)
- Per-sample: 5-10 minutes
- Total for 20 samples: **2-4 hours**

---

## Option 2: Full API Integration (Automated Validation)

### Overview
Integrate EcoTaxa API into our pipeline for automated classification comparison.

### Architecture
```
┌─────────────────────────────────────────────┐
│         Raspberry Pi System                 │
├─────────────────────────────────────────────┤
│  1. Capture Image                           │
│  2. Preprocess                              │
│  3. Classify with Local Model               │
│  4. Save Local Results                      │
│  5. Upload to EcoTaxa API (async)           │
│  6. Retrieve EcoTaxa Classifications        │
│  7. Compare & Log Differences               │
│  8. Display Both Results in Dashboard       │
└─────────────────────────────────────────────┘
```

### Implementation Steps

1. **Install EcoTaxa Python Client**
   ```bash
   pip install git+https://github.com/ecotaxa/ecotaxa_py_client.git
   ```

2. **Add EcoTaxa Module to Our Pipeline**
   ```python
   # modules/ecotaxa_integration.py

   class EcoTaxaModule(PipelineModule):
       def __init__(self, config):
           super().__init__(config)
           self.client = EcoTaxaClient(
               username=config['username'],
               password=config['password']
           )
           self.project_id = config.get('project_id')

       def process(self, input_data):
           """Upload to EcoTaxa and get classification"""
           image = input_data['image']
           metadata = input_data['metadata']

           # Upload image
           ecotaxa_result = self.client.classify_image(
               image=image,
               metadata=metadata,
               project_id=self.project_id
           )

           return {
               'status': 'success',
               'ecotaxa_class': ecotaxa_result['class'],
               'ecotaxa_confidence': ecotaxa_result['confidence'],
               'ecotaxa_object_id': ecotaxa_result['object_id']
           }
   ```

3. **Modify Pipeline Manager**
   ```python
   # pipeline/manager.py

   def execute_pipeline(self, acquisition_params):
       # ... existing steps ...

       # After classification
       r4 = self.modules["classification"].process(...)

       # Optional: Compare with EcoTaxa
       if self.config.get('enable_ecotaxa_validation'):
           r_ecotaxa = self.modules["ecotaxa"].process({
               'image': r2['processed_image'],
               'metadata': r1['metadata']
           })

           # Compare results
           comparison = self.compare_classifications(
               local=r4['predictions'],
               ecotaxa=r_ecotaxa
           )

           # Add to results
           results['ecotaxa_comparison'] = comparison
   ```

4. **Add to Config**
   ```yaml
   # config/config.yaml

   ecotaxa:
     enabled: true
     username: "your_username"
     password: "your_password"  # Or use env variable
     project_id: 12345
     async_mode: true  # Don't block main pipeline
     comparison_only: true  # Don't show to user, just log
   ```

### Pros
- ✅ **Automated** - runs in background
- ✅ **Scalable** - can process many samples
- ✅ **Real-time comparison** - immediate feedback
- ✅ **Continuous validation** - every sample validated
- ✅ **Data collection** - build comparison dataset

### Cons
- ❌ **Complex** - significant coding required
- ❌ **Internet required** - won't work offline
- ❌ **API rate limits** - may hit limits with many samples
- ❌ **Latency** - adds delay to pipeline
- ❌ **Dependency** - system depends on external API

### Recommended For
- **Post-hackathon** development
- **Continuous validation** in field deployment
- **Data collection** for model improvement

### Time Estimate
- Development: **2-3 days**
- Testing: **1 day**
- Total: **3-4 days**

---

## Option 3: Download EcoTaxa Dataset (Training Data)

### Overview
Use EcoTaxa to export validated training data, train our own model, deploy independently.

### Implementation Steps

1. **Access Public Datasets**
   - Browse EcoTaxa public projects
   - Find relevant plankton datasets
   - Note project IDs

2. **Export Data via API or Web**
   ```python
   # Export dataset
   from ecotaxa_py_client.api import projects_api

   proj_api = projects_api.ProjectsApi(client)

   # Export project data
   export_job = proj_api.project_export(
       project_id=12345,
       export_type='detail'  # Includes images and metadata
   )

   # Download when ready
   download_url = wait_for_export(export_job['job_id'])
   download_dataset(download_url, './training_data/')
   ```

3. **Organize for Training**
   ```
   training_data/
   ├── copepod/
   │   ├── img_001.jpg
   │   ├── img_002.jpg
   ├── diatom/
   │   ├── img_001.jpg
   ├── dinoflagellate/
   │   └── ...
   └── metadata.csv
   ```

4. **Train Model**
   ```python
   # Use EcoTaxa data to train our model
   from modules.classification import train_model

   model = train_model(
       data_dir='./training_data',
       architecture='efficientnet-lite',
       epochs=50,
       augmentation=True
   )

   # Convert to TFLite
   convert_to_tflite(model, 'models/plankton_ecotaxa_v1.tflite')
   ```

5. **Deploy to Raspberry Pi**
   - Copy TFLite model to Pi
   - No internet required
   - Fast inference

### Pros
- ✅ **High-quality labels** - validated by experts
- ✅ **Large dataset** - access to millions of images
- ✅ **Offline capable** - no runtime dependency
- ✅ **Full control** - our own model
- ✅ **Fast inference** - local processing

### Cons
- ❌ **One-time** - not continuous learning
- ❌ **Storage** - large datasets (GBs)
- ❌ **Training time** - requires GPU
- ❌ **Model selection** - need to choose right classes

### Recommended For
- **Model training** before hackathon
- **Baseline model** for prototype
- **Offline deployment** in field

### Time Estimate
- Dataset download: **2-4 hours**
- Data preparation: **4-6 hours**
- Model training: **8-12 hours** (with GPU)
- Total: **1-2 days**

---

## Option 4: Hybrid Approach (Recommended)

### Overview
Combine local model with optional EcoTaxa validation for best of both worlds.

### Architecture
```
┌────────────────────────────────────────────────┐
│               Field Deployment                  │
├────────────────────────────────────────────────┤
│  Capture → Preprocess → Segment                │
│              ↓                                  │
│      [Local TFLite Model]                      │
│              ↓                                  │
│    Classification (Fast, Offline)              │
│              ↓                                  │
│    Counting & Analytics                        │
│              ↓                                  │
│         Export Results                          │
│                                                 │
│  Optional (when internet available):           │
│    → Upload to EcoTaxa                         │
│    → Get validation                            │
│    → Log comparison                            │
│    → Retrain model periodically                │
└────────────────────────────────────────────────┘
```

### Implementation Strategy

#### Phase 1: Training (Pre-Deployment)
1. Download EcoTaxa datasets
2. Train local model
3. Validate accuracy against EcoTaxa
4. Deploy to Raspberry Pi

#### Phase 2: Field Operation (Offline)
1. Run local model only
2. Store images and predictions locally
3. No internet required
4. Fast, reliable operation

#### Phase 3: Validation (When Online)
1. Batch upload samples to EcoTaxa
2. Compare local predictions with EcoTaxa
3. Identify discrepancies
4. Collect challenging samples

#### Phase 4: Improvement (Periodic)
1. Retrain model with new data
2. Deploy updated model
3. Continuous improvement cycle

### Configuration
```yaml
# config/config.yaml

classification:
  model_path: "./models/plankton_ecotaxa_v1.tflite"
  class_names: ["Copepod", "Diatom", "Dinoflagellate", "Ciliate", "Other"]
  confidence_threshold: 0.7
  source: "ecotaxa_trained"  # Document where model came from

ecotaxa_validation:
  enabled: true
  mode: "async"  # Don't block main pipeline
  upload_threshold: 0.5  # Only upload low-confidence predictions
  batch_mode: true  # Upload in batches when online
  project_id: 12345
  validation_frequency: "weekly"  # How often to validate

export:
  include_ecotaxa_comparison: true  # Add comparison to export
```

### Pros
- ✅ **Best accuracy** - trained on EcoTaxa data
- ✅ **Offline capable** - works without internet
- ✅ **Continuous validation** - improves over time
- ✅ **Flexible** - can work with or without EcoTaxa
- ✅ **Credible** - shows validation process

### Cons
- ❌ **Complex** - most development effort
- ❌ **Time-consuming** - requires all previous steps
- ❌ **Maintenance** - need to manage updates

### Recommended For
- **Production system** (post-hackathon)
- **Long-term deployment**
- **Research-grade accuracy**

### Time Estimate
- **1 week** full implementation
- But can be done in phases

---

## Option 5: Reference Only (Demo/Presentation)

### Overview
Simply mention EcoTaxa in presentation without actual integration.

### What to Show
1. **Slide 1: Data Validation**
   - "We validated our approach using EcoTaxa platform"
   - Show EcoTaxa homepage screenshot
   - "650M+ validated images from 850+ institutions"

2. **Slide 2: Comparison**
   - "Manual validation of 20 samples against EcoTaxa"
   - Show comparison table:
     ```
     Sample | Our Model | EcoTaxa | Match?
     001    | Copepod   | Copepod | ✓
     002    | Diatom    | Diatom  | ✓
     003    | Unknown   | Ciliate | ✗
     ```

3. **Slide 3: Future Integration**
   - "Planned integration for continuous validation"
   - Show architecture diagram

### Pros
- ✅ **Zero effort** - just presentation
- ✅ **Adds credibility** - reference to established platform
- ✅ **No technical risk** - doesn't affect system

### Cons
- ❌ **No actual validation** - just claims
- ❌ **Limited impact** - judges may want to see proof

### Recommended For
- **Time-constrained** situations
- **Backup plan** if integration fails
- **Initial pitch** before implementation

### Time Estimate
- **1 hour** for slides

---

## 🎯 Recommendation for First Prototype

### For SIH Hackathon (5 days):

**Best Approach: Option 1 + Option 5**

#### Week 1-2 (Before Hackathon):
1. ✅ Download EcoTaxa public dataset (Option 3)
2. ✅ Train local model
3. ✅ Deploy to Raspberry Pi

#### Day 1-2 (Hackathon):
1. ✅ Focus on core pipeline
2. ✅ Get local classification working
3. ✅ Don't integrate EcoTaxa API yet

#### Day 3 (Hackathon):
1. ✅ Upload 20 sample images to EcoTaxa manually (Option 1)
2. ✅ Compare results
3. ✅ Document accuracy

#### Day 4-5 (Hackathon):
1. ✅ Create comparison slides (Option 5)
2. ✅ Show validation process
3. ✅ Demo system without EcoTaxa dependency

### After Hackathon (If Continuing):

**Implement Option 4 (Hybrid)**
- Week 1: API integration
- Week 2: Async validation
- Week 3: Continuous improvement

---

## 📋 Quick Decision Matrix

**If you have...**

- **< 1 day**: Option 5 (Reference only)
- **1-2 days**: Option 1 (Manual validation)
- **3-4 days**: Option 3 (Download dataset, train model)
- **1 week**: Option 4 (Hybrid approach)
- **Post-hackathon**: Option 2 or 4 (API integration)

**If you need...**

- **Offline capability**: Option 3 or 4
- **Credibility only**: Option 1 or 5
- **Continuous validation**: Option 2 or 4
- **Best accuracy**: Option 3 or 4
- **Simplest approach**: Option 1 or 5

---

## 🚀 Implementation Checklist

### Pre-Hackathon (Week 1-2)
- [ ] Create EcoTaxa account
- [ ] Explore web interface with sample images
- [ ] Download public plankton datasets
- [ ] Train initial model on EcoTaxa data
- [ ] Test accuracy on validation set

### Hackathon Day 1-2
- [ ] Deploy local model to Pi
- [ ] Test inference speed
- [ ] Integrate into pipeline
- [ ] Verify offline operation

### Hackathon Day 3
- [ ] Upload 20 samples to EcoTaxa (manual)
- [ ] Wait for ML predictions
- [ ] Download results
- [ ] Compare with our model

### Hackathon Day 4-5
- [ ] Create comparison table/slides
- [ ] Document methodology
- [ ] Prepare demo
- [ ] Test presentation flow

---

**Recommendation**: Start with **Option 1** (manual validation) for hackathon demo. It adds credibility with minimal risk. After hackathon, implement **Option 4** (hybrid) for production deployment.
