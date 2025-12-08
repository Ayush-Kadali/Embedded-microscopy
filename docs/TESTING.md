# Testing Guide - Simulation vs Prototype

**Test Results**: 18/19 tests passing (95% pass rate)

**Purpose**: Explain how we test now (simulation) vs how we'll test with real prototype

---

## Current Testing Status

### Test Execution
```bash
source .venv/bin/activate
pytest tests/test_all_modules.py -v
```

**Results**:
- Total tests: 19
- Passed: 18 (95%)
- Failed: 1 (magnification validation - edge case)

### What We Test

**Contract Compliance**:
- All modules have correct input/output structure
- All required fields present
- All field types correct
- All value ranges valid

**Integration**:
- Module outputs match next module's inputs
- Full pipeline executes end-to-end
- No contract violations during integration

**Error Handling**:
- Modules return proper error status
- Error messages present when status='error'
- Invalid inputs rejected

---

## Simulation Testing (Current Approach)

### How It Works

**Synthetic Data Generation**:
- Acquisition: Generates random synthetic images with organism-like blobs
- Classification: Returns predictions based on simple heuristics
- All other modules: Use real algorithms on synthetic data

### What We Validate

**Module Contracts**:
```python
# For each module, we test:
1. Input validation (correct format)
2. Output validation (matches contract)
3. Type checking (all fields correct type)
4. Range checking (values in valid ranges)
5. Integration (output → next input works)
```

### Example: Acquisition Module Simulation

**Current (Simulation)**:
```python
def _capture_image(self, exposure_ms):
    # Generate synthetic image
    img = np.random.randint(200, 230, (2028, 2028, 3), dtype=np.uint8)

    # Add random "organisms" (dark blobs)
    for _ in range(random.randint(5, 20)):
        center_x = random.randint(100, 1928)
        center_y = random.randint(100, 1928)
        radius = random.randint(20, 80)
        # Draw blob
        ...

    return img
```

**Validates**:
- Image is correct shape (H, W, 3)
- Image is uint8 RGB
- Metadata calculated correctly
- Resolution calibration formula works

**Does NOT validate**:
- Real camera exposure works
- Real camera focus works
- Actual image quality from microscope

### Example: Classification Module Simulation

**Current (Simulation)**:
```python
def _predict(self, image_crop):
    # Simple heuristic-based prediction
    logits = np.random.randn(num_classes)

    # Bias based on features
    gray = cv2.cvtColor(image_crop, cv2.COLOR_RGB2GRAY)
    if np.mean(gray) < 100:
        logits[0] += 3.0  # Dark = first class

    # Softmax
    probs = softmax(logits)
    return probs
```

**Validates**:
- Prediction structure correct
- Confidence scores sum to 1.0
- Top-K predictions work
- Integration with counting module works

**Does NOT validate**:
- Actual classification accuracy
- Real TFLite model performance
- Species identification correctness

---

## Prototype Testing (Real System Approach)

### How It Will Work

**Real Hardware & Data**:
- Raspberry Pi HQ Camera captures real images
- Real microscope at calibrated magnification
- Trained TFLite model classifies real plankton
- GPS module provides real coordinates

### What We'll Validate

**Hardware Integration**:
```python
# Acquisition with real camera
from picamera2 import Picamera2

def _capture_image(self, exposure_ms):
    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start()

    # Set exposure
    picam2.set_controls({"ExposureTime": exposure_ms * 1000})

    # Capture
    image = picam2.capture_array()
    picam2.stop()

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
```

**Tests**:
1. Camera initializes correctly
2. Exposure time affects brightness
3. Focus position changes sharpness
4. Image quality meets requirements
5. Calibration accurate across magnifications

**Model Accuracy**:
```python
# Classification with trained model
import tensorflow as tf

def _load_model(self):
    self.interpreter = tf.lite.Interpreter(
        model_path=self.config['model_path']
    )
    self.interpreter.allocate_tensors()

def _predict(self, image_crop):
    # Preprocess
    input_data = preprocess(image_crop)

    # Inference
    self.interpreter.set_tensor(input_details[0]['index'], input_data)
    self.interpreter.invoke()
    output = self.interpreter.get_tensor(output_details[0]['index'])

    return output[0]
```

**Tests**:
1. Model loads correctly
2. Inference speed <3s for 20 organisms
3. Classification accuracy >70% on validation set
4. Handles edge cases (0 organisms, many organisms, poor image)
5. Confidence scores calibrated

---

## Transition Plan: Simulation to Prototype

### Day 1-2 (Hackathon Start)

**Use**: Simulation testing

**Why**:
- No real hardware available yet
- No trained model yet
- Validates architecture and contracts
- Enables parallel development

**Tests**:
- Contract compliance
- Integration between modules
- Error handling
- Pipeline orchestration

### Day 2-3 (After Evaluator Feedback)

**Integrate**: Real components as they become available

**Priority Order**:
1. Classification model (CRITICAL)
   - Replace stub with trained TFLite model
   - Test accuracy on validation set
   - Measure inference speed

2. Real test images (HIGH)
   - Download WHOI plankton dataset
   - Replace synthetic images
   - Test with diverse real images

3. Dashboard (HIGH)
   - Integrate Streamlit UI
   - Test with real results
   - User acceptance testing

### Day 4-5 (Final Testing)

**Add**: Hardware if available

**Components**:
1. Raspberry Pi camera
2. GPS module (optional)
3. Microscope setup

**Tests**:
- End-to-end with real hardware
- Field testing with water samples
- Performance benchmarking
- Accuracy validation

---

## Test Categories

### Unit Tests (Module-Specific)

**Purpose**: Test each module independently

**Location**: `tests/test_all_modules.py`

**Run**:
```bash
pytest tests/test_all_modules.py::TestAcquisitionModule -v
pytest tests/test_all_modules.py::TestClassificationModule -v
```

**Example**:
```python
def test_classification_output_contract():
    """Test classification returns correct structure."""
    module = ClassificationModule(config)
    result = module.process(input_data)

    assert 'predictions' in result
    assert len(result['predictions']) == len(input_masks)
    for pred in result['predictions']:
        assert 0.0 <= pred['confidence'] <= 1.0
```

### Integration Tests

**Purpose**: Test modules work together

**Location**: `tests/test_all_modules.py::TestIntegration`

**Tests**:
- Acquisition → Preprocessing
- Preprocessing → Segmentation
- Segmentation → Classification
- Classification → Counting
- Counting → Analytics
- Analytics → Export

**Example**:
```python
def test_module_chain_contracts():
    """Test each module's output feeds correctly to next."""
    # Run acquisition
    acq_result = acq_module.process(acq_input)

    # Feed to preprocessing
    prep_result = prep_module.process({
        'image': acq_result['image'],  # Uses output from previous
        ...
    })

    # Continue chain...
```

### End-to-End Tests

**Purpose**: Test complete pipeline

**Location**: `main.py` or `pytest tests/test_all_modules.py::test_full_pipeline_integration`

**Run**:
```bash
python main.py
```

**Validates**:
- Pipeline runs without crashes
- Results generated
- Files exported
- All modules integrated

### Accuracy Validation (Prototype Only)

**Purpose**: Measure real-world performance

**Location**: `tests/test_accuracy.py` (to be created)

**Requires**:
- Ground truth labeled dataset
- Real test images
- Trained model

**Metrics**:
```python
def test_classification_accuracy():
    """Test classification accuracy on validation set."""
    correct = 0
    total = 0

    for image, true_label in validation_set:
        pred = classifier.predict(image)
        if pred['class_name'] == true_label:
            correct += 1
        total += 1

    accuracy = correct / total
    assert accuracy > 0.70  # Target: >70%
```

---

## Testing Checklist

### Current (Simulation) - Day 1-2

**Contract Testing**:
- [ ] All modules accept valid input
- [ ] All modules produce valid output
- [ ] All required fields present
- [ ] All field types correct
- [ ] All value ranges valid

**Integration Testing**:
- [ ] Module outputs feed to next inputs
- [ ] Full pipeline runs end-to-end
- [ ] No contract violations
- [ ] Error propagation works

**Regression Testing**:
- [ ] pytest runs without failures
- [ ] main.py completes successfully
- [ ] Results files generated

### Prototype Testing - Day 3-5

**Model Accuracy**:
- [ ] Classification accuracy >70%
- [ ] Precision and recall measured
- [ ] Confusion matrix analyzed
- [ ] Edge cases handled

**Performance**:
- [ ] Total pipeline <30s per image
- [ ] Classification <3s for 20 organisms
- [ ] Memory usage acceptable on Pi
- [ ] No memory leaks

**Hardware Integration**:
- [ ] Camera captures clear images
- [ ] Calibration accurate
- [ ] GPS coordinates correct
- [ ] All sensors working

**User Acceptance**:
- [ ] Dashboard intuitive
- [ ] Results accurate
- [ ] Export formats useful
- [ ] Error messages clear

---

## Test Data Requirements

### Simulation (Current)

**Synthetic Images**:
- Generated on-the-fly
- Random organism positions
- Controlled size distribution
- Unlimited quantity

**Advantage**: No data collection needed

**Limitation**: Not realistic

### Prototype

**Real Images**:
- WHOI plankton dataset (Kaggle)
- 20-50 diverse test images
- Include: clean, noisy, few organisms, many organisms
- Ground truth labels

**Training Data**:
- 1000+ labeled plankton images
- 5+ classes minimum
- Balanced distribution

**Validation Data**:
- 200+ labeled images
- Never seen during training
- Representative of real deployment

---

## Running Tests

### Quick Test (Main Pipeline)
```bash
source .venv/bin/activate
python main.py
```
Expected: Completes without errors

### Comprehensive Test (All Modules)
```bash
pytest tests/test_all_modules.py -v
```
Expected: 18-19 tests pass

### Individual Module Test
```bash
pytest tests/test_all_modules.py::TestClassificationModule -v
```

### With Coverage
```bash
pytest tests/test_all_modules.py --cov=modules --cov-report=html
open htmlcov/index.html
```

### Fast Test (Simulation Only)
```bash
python examples/test_individual_module.py
```

---

## Test Maintenance

### When to Update Tests

**Contract Changes**:
- If module contract changes, update tests immediately
- Update `MODULE_CONTRACTS.md` first
- Then update tests to match
- Then update implementation

**New Features**:
- Add new test for new functionality
- Ensure backwards compatibility
- Don't break existing tests

**Bug Fixes**:
- Add test that reproduces bug
- Fix bug
- Verify test now passes

### Test Organization

```
tests/
├── test_all_modules.py      # Comprehensive module tests (current)
├── test_accuracy.py          # Accuracy validation (prototype)
├── test_performance.py       # Performance benchmarks (prototype)
├── test_hardware.py          # Hardware integration (prototype)
└── test_example.py           # Example tests (reference)
```

---

## Summary

### Simulation Testing (Day 1-2)
- **What**: Synthetic data, stub implementations
- **Tests**: Contracts, integration, structure
- **Purpose**: Enable parallel development, validate architecture
- **Status**: 95% passing (18/19 tests)

### Prototype Testing (Day 3-5)
- **What**: Real hardware, trained model, real data
- **Tests**: Accuracy, performance, user acceptance
- **Purpose**: Validate real-world functionality
- **Status**: To be implemented as components become available

### Transition
- Start with simulation (validates design)
- Add real components incrementally
- Keep simulation tests for regression
- Add prototype tests for accuracy

**Current readiness**: System validated via simulation, ready for real components

---

## Quick Reference

```bash
# Run all tests
pytest tests/test_all_modules.py -v

# Run specific test
pytest tests/test_all_modules.py::TestClassificationModule::test_output_contract -v

# Run with verbose output
pytest tests/test_all_modules.py -vv

# Run and stop on first failure
pytest tests/test_all_modules.py -x

# Run integration tests only
pytest tests/test_all_modules.py::TestIntegration -v
```

**Test passing**: Contracts validated, integration working, ready for real data
