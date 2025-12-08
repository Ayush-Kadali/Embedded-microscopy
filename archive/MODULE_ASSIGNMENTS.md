# Module Assignment Template

Use this template to assign modules to team members and track progress.

## Team Member Assignments

### Module 1: Image Acquisition
- **Assigned to**: _________________
- **GitHub username**: _________________
- **Status**: Not Started / In Progress / Complete
- **Branch**: `feature/acquisition`
- **Key Tasks**:
  - [ ] Integrate Picamera2 library
  - [ ] Calibrate µm/pixel for microscope magnification settings
  - [ ] Add GPS module integration (gpsd)
  - [ ] Implement auto-exposure algorithm
  - [ ] Add error handling for camera failures
  - [ ] Write unit tests
- **Dependencies**: Raspberry Pi HQ Camera, GPS module (optional)
- **Estimated completion**: _________________
- **Notes**:

---

### Module 2: Preprocessing
- **Assigned to**: _________________
- **GitHub username**: _________________
- **Status**: Not Started / In Progress / Complete
- **Branch**: `feature/preprocessing`
- **Key Tasks**:
  - [ ] Benchmark denoise methods (gaussian, bilateral, NLM)
  - [ ] Optimize background correction for plankton images
  - [ ] Implement flatfield correction
  - [ ] Add image quality assessment
  - [ ] Optimize performance for Raspberry Pi
  - [ ] Write unit tests
- **Dependencies**: OpenCV, test images
- **Estimated completion**: _________________
- **Notes**:

---

### Module 3: Segmentation
- **Assigned to**: _________________
- **GitHub username**: _________________
- **Status**: Not Started / In Progress / Complete
- **Branch**: `feature/segmentation`
- **Key Tasks**:
  - [ ] Fine-tune watershed parameters
  - [ ] Research instance segmentation models (YOLO, Mask R-CNN)
  - [ ] Train/convert model to TFLite if using model-based approach
  - [ ] Implement overlap handling
  - [ ] Benchmark accuracy on test dataset
  - [ ] Write unit tests
- **Dependencies**: Labeled segmentation dataset, OpenCV
- **Estimated completion**: _________________
- **Notes**:

---

### Module 4: Classification
- **Assigned to**: _________________
- **GitHub username**: _________________
- **Status**: Not Started / In Progress / Complete
- **Branch**: `feature/classification`
- **Key Tasks**:
  - [ ] Collect and label training dataset (1000+ images)
  - [ ] Train CNN classifier (MobileNetV2, EfficientNet)
  - [ ] Convert model to TFLite and quantize (INT8)
  - [ ] Benchmark inference speed on Raspberry Pi
  - [ ] Implement confidence calibration
  - [ ] Write unit tests
- **Dependencies**: Labeled training data, TensorFlow/PyTorch
- **Estimated completion**: _________________
- **Notes**:

---

### Module 5: Counting & Sizing
- **Assigned to**: _________________
- **GitHub username**: _________________
- **Status**: Complete (working implementation)
- **Branch**: `main`
- **Key Tasks**:
  - [ ] Validate size estimation accuracy with known samples
  - [ ] Add spatial distribution analysis
  - [ ] Implement outlier detection
  - [ ] Add size calibration validation tools
  - [ ] Write additional tests
- **Dependencies**: Calibration samples
- **Estimated completion**: _________________
- **Notes**: Basic implementation complete, needs validation

---

### Module 6: Analytics
- **Assigned to**: _________________
- **GitHub username**: _________________
- **Status**: Complete (working implementation)
- **Branch**: `main`
- **Key Tasks**:
  - [ ] Add additional diversity metrics (Pielou's evenness)
  - [ ] Implement time-series trend analysis
  - [ ] Research HAB prediction models
  - [ ] Validate diversity calculations
  - [ ] Add ecological alert system
  - [ ] Write additional tests
- **Dependencies**: Historical plankton count data
- **Estimated completion**: _________________
- **Notes**: Basic implementation complete, needs enhancement

---

### Module 7: Export & Dashboard
- **Assigned to**: _________________
- **GitHub username**: _________________
- **Status**: Partial (CSV/JSON complete, dashboard stub)
- **Branch**: `feature/dashboard`
- **Key Tasks**:
  - [ ] Build Streamlit dashboard with interactive plots
  - [ ] Add Folium map visualization for GPS data
  - [ ] Implement real-time plotting
  - [ ] Add database export (SQLite/PostgreSQL)
  - [ ] Create data archival system
  - [ ] Write unit tests
- **Dependencies**: Streamlit, Folium, database (optional)
- **Estimated completion**: _________________
- **Notes**: CSV/JSON export working, dashboard needs implementation

---

## Support Roles

### Integration & Testing Lead
- **Assigned to**: _________________
- **Responsibilities**:
  - Ensure all modules integrate correctly
  - Run end-to-end tests
  - Maintain CI/CD pipeline
  - Review pull requests for contract compliance

### Data Collection Lead
- **Assigned to**: _________________
- **Responsibilities**:
  - Collect training data for classification
  - Label images (segmentation + classification)
  - Collect calibration samples
  - Gather historical plankton count data

### Hardware Setup Lead
- **Assigned to**: _________________
- **Responsibilities**:
  - Set up Raspberry Pi with camera
  - Configure GPS module
  - Build/configure microscope setup
  - Create deployment image for Raspberry Pi OS

### Documentation Lead
- **Assigned to**: _________________
- **Responsibilities**:
  - Maintain developer documentation
  - Write user manual
  - Create tutorial videos
  - Update API documentation

---

## Development Guidelines

### Branch Naming
- Feature branches: `feature/<module-name>`
- Bug fixes: `bugfix/<issue-description>`
- Hotfixes: `hotfix/<issue-description>`

### Commit Messages
```
<module>: <brief description>

<detailed description if needed>

- Bullet points for changes
```

Example:
```
classification: Add MobileNetV2 model with quantization

Trained on 1500 labeled plankton images with 5 classes.
Quantized to INT8 for edge deployment.

- 92% validation accuracy
- 15ms inference time on Pi4
- Model size: 4.2MB
```

### Pull Request Process
1. Create feature branch from `main`
2. Implement your module following the contract
3. Write unit tests (aim for >80% coverage)
4. Test integration with full pipeline
5. Update documentation if contract changes
6. Create PR with clear description
7. Request review from Integration Lead
8. Address feedback
9. Merge to `main` after approval

### Code Review Checklist
- [ ] Contract unchanged (or documented if changed)
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Code follows Python style guide (PEP 8)
- [ ] Docstrings updated
- [ ] No hardcoded paths or credentials
- [ ] Performance acceptable on Raspberry Pi

---

## Communication

### Standup Schedule
- **When**: Daily at _________________
- **Where**: _________________
- **Format**: What you did, what you're doing, any blockers

### Weekly Sync
- **When**: Weekly on _________________
- **Where**: _________________
- **Agenda**: Progress review, integration issues, planning

### Slack/Discord Channels
- `#general` - General discussion
- `#dev-acquisition` - Acquisition module
- `#dev-classification` - Classification/ML
- `#dev-dashboard` - Dashboard/visualization
- `#help` - Ask questions
- `#integration` - Integration testing

---

## Milestones

### Sprint 1 (Week 1-2): Setup & Stubs
- [x] Pipeline architecture complete
- [x] All module interfaces defined
- [x] Stub implementations working
- [ ] Team assignments complete
- [ ] Dev environment set up on all machines

### Sprint 2 (Week 3-4): Core Implementation
- [ ] Acquisition: Camera integration
- [ ] Classification: Model training started
- [ ] Preprocessing: Optimized for plankton
- [ ] Segmentation: Method comparison complete

### Sprint 3 (Week 5-6): Integration & Testing
- [ ] All modules integrated
- [ ] End-to-end tests passing
- [ ] Performance benchmarks met
- [ ] Dashboard v1 complete

### Sprint 4 (Week 7-8): Optimization & Deployment
- [ ] Model quantization complete
- [ ] Performance optimized for Pi
- [ ] Documentation complete
- [ ] Raspberry Pi image ready
- [ ] Final testing and validation

---

## Resources

### Datasets
- Plankton classification: [WHOI Plankton Dataset](https://www.kaggle.com/datasets/vencerlanz09/sea-animals-image-dataset)
- Segmentation: [PlanktonNet](https://www.seanoe.org/data/00446/55741/)

### Hardware Vendors
- Raspberry Pi: [raspberrypi.com](https://www.raspberrypi.com/)
- GPS modules: Multiple vendors

### Reference Papers
- Plankton classification with CNNs
- Marine biodiversity monitoring
- Edge AI deployment strategies

---

**Last Updated**: [Date]
**Updated By**: [Name]
