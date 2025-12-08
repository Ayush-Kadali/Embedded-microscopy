# Modular AI Microscopy System – Architecture \& Implementation Guide

## Project overview

Develop an embedded intelligent microscopy system for identification and counting of microscopic marine organisms on low‑resource hardware such as Raspberry Pi. The system should process microscope images end‑to‑end on device: capture → preprocess → segment → classify → count → analytics → export, producing geo‑tagged, time‑stamped CSV reports and a small dashboard.

The core design goal is strict modularity: each stage is a replaceable module with a stable, documented interface so that internal changes in one module never require changes in the rest of the pipeline.

***

## Modularity principles

### High cohesion, low coupling

- Each module has one clear responsibility (high cohesion) such as “segmentation” or “counting”, and does not mix unrelated concerns.
- Modules do not depend on each other’s internals and communicate only via typed input/output contracts (low coupling).


### Standard input/output contracts

For every module define:

- Input schema: required keys, types, units and validation rules.
- Output schema: required keys, types and guarantees (e.g., shape of arrays, value ranges).
- Error model: `status`, `error_message`, and optional `error_type` fields so the pipeline can treat all modules uniformly.


### Substitutability

A module can be replaced if it:

- Respects the same input/output schema.
- Handles errors using the shared error model.
- Passes the same contract tests (unit tests on interfaces rather than implementation).

***

## End‑to‑end pipeline

Conceptual dataflow:

```text
[Raw Image] 
    → [Preprocessing] 
    → [Segmentation] 
    → [Classification] 
    → [Counting] 
    → [Analytics] 
    → [Export]
```

Each bracket is a module; the pipeline manager just wires modules together and handles control flow, logging and error propagation.

***

## Module 1 – Image acquisition

**Responsibility**: Capture raw microscope images plus physical metadata.

**Input contract (Python type sketch)**

```python
AcquisitionInput = dict(
    magnification=float,          # 0.7–4.5 (Seeed 300X lens range)[file:1]
    exposure_ms=int,              # exposure in ms
    focus_position=int | None,    # optional motor stage position
    capture_metadata=dict(
        timestamp=str,            # ISO 8601
        gps_lat=float | None,
        gps_lon=float | None,
        operator_id=str | None,
    ),
)
```

**Output contract**

```python
AcquisitionOutput = dict(
    status=str,                   # "success" | "error"
    error_message=str | None,
    image="np.ndarray[H, W, 3]",  # uint8 RGB
    metadata=dict(
        capture_id=str,           # UUID
        timestamp=str,
        gps_coordinates=list[float] | None,  # [lat, lon]
        magnification=float,
        exposure_ms=int,
        resolution_um_per_px=float,          # ~1.55 / M for Pi HQ sensor[file:1]
        fov_mm=list[float],       # [width_mm, height_mm][file:1]
        sensor_temp_c=float | None,
    ),
)
```

**Implementation notes**

- Backed by Picamera2/libcamera on Raspberry Pi OS Lite; calibration code can compute µm/px and FOV from magnification.
- All hardware details are encapsulated here so the rest of the pipeline never touches camera drivers.

***

## Module 2 – Preprocessing

**Responsibility**: Denoise, normalize, and correct illumination to prepare images for segmentation.

**Input contract**

```python
PreprocessInput = dict(
    image="np.ndarray[H, W, 3]",
    preprocessing_config=dict(
        denoise_method=str,           # "gaussian" | "bilateral" | "nlm"
        normalize=bool,
        background_correction=bool,
        flatfield_correction=bool,
        illumination_profile="np.ndarray | None",
    ),
)
```

**Output contract**

```python
PreprocessOutput = dict(
    status=str,
    error_message=str | None,
    processed_image="np.ndarray[H, W, 3]",
    preprocessing_stats=dict(
        mean_intensity=float,
        std_intensity=float,
        snr_db=float | None,
        background_level=float | None,
    ),
)
```

**Implementation notes**

- Use OpenCV filters for denoise and background subtraction; maintain original image size and dtype.
- Keep algorithm choice configurable to allow future swaps without touching segmentation.

***

## Module 3 – Segmentation

**Responsibility**: Detect and isolate individual organisms as masks or bounding boxes.

**Input contract**

```python
SegmentationInput = dict(
    image="np.ndarray[H, W, 3]",
    segmentation_config=dict(
        method=str,                   # "threshold" | "watershed" | "instance_seg"
        min_area_px=int,
        max_area_px=int,
        handle_overlaps=bool,
        model_path=str | None,
    ),
)
```

**Output contract**

```python
SegmentationOutput = dict(
    status=str,
    error_message=str | None,
    masks=list["np.ndarray[H, W]"],   # boolean masks
    bounding_boxes=list[dict(x=int, y=int, w=int, h=int)],
    centroids=list[tuple[int, int]],
    areas_px=list[int],
    num_detected=int,
)
```

**Implementation notes**

- Simple path: grayscale → adaptive/Otsu threshold → connected components, filtered by area.
- Advanced path: small instance‑segmentation model for severe overlaps, still returning the same contract.

***

## Module 4 – Classification

**Responsibility**: Classify each segmented organism at genus/species or morphological type.

**Input contract**

```python
ClassificationInput = dict(
    image="np.ndarray[H, W, 3]",
    masks=list["np.ndarray[H, W]"],
    bounding_boxes=list[dict],
    classification_config=dict(
        model_path=str,              # TFLite/ONNX/PyTorch model
        class_names=list[str],
        confidence_threshold=float,
        top_k=int,
    ),
)
```

**Output contract**

```python
ClassificationOutput = dict(
    status=str,
    error_message=str | None,
    predictions=list[dict(
        organism_id=int,
        class_name=str,
        confidence=float,
        top_k_predictions=list[dict(class_name=str, score=float)],
    )],
    model_metadata=dict(
        model_name=str,
        version=str,
        input_size=tuple[int, int],
        inference_time_ms=float,
    ),
)
```

**Implementation notes**

- Crop organisms from the preprocessed image using bounding boxes, resize to model input, run quantized CNN (e.g., MobileNet/ResNet‑lite).
- Classification module is fully decoupled from segmentation details except for masks/boxes and is therefore easily swappable with new models.

***

## Module 5 – Counting \& sizing

**Responsibility**: Aggregate counts per class and compute approximate organism sizes in micrometers.

**Input contract**

```python
CountingInput = dict(
    predictions=list[dict],
    areas_px=list[int],
    centroids=list[tuple[int, int]],
    metadata=dict,  # from acquisition
    counting_config=dict(
        confidence_threshold=float,
        size_range_um=list[float],    # [min_um, max_um]
        count_by_class=bool,
    ),
)
```

**Output contract**

```python
CountingOutput = dict(
    status=str,
    error_message=str | None,
    counts_by_class=dict[str, int],
    total_count=int,
    size_distribution=dict[         # per class
        str, dict(
            mean_um=float,
            std_um=float,
            histogram=list[int],
        )
    ],
    organisms=list[dict(
        organism_id=int,
        class_name=str,
        confidence=float,
        size_um=float,
        centroid_px=tuple[int, int],
        centroid_um=tuple[float, float],
    )],
)
```

**Implementation notes**

- Convert area in pixels to equivalent diameter in µm using calibrated µm/px from acquisition.
- Do not recompute classification; only aggregate and transform data, keeping responsibilities clean.

***

## Module 6 – Edge analytics

**Responsibility**: Compute ecological metrics and bloom flags from counts.

**Input contract**

```python
AnalyticsInput = dict(
    counts_by_class=dict[str, int],
    organisms=list[dict],
    historical_data=list[dict] | None,
    analytics_config=dict(
        compute_diversity=bool,
        compute_composition=bool,
        bloom_thresholds=dict[str, int],
    ),
)
```

**Output contract**

```python
AnalyticsOutput = dict(
    status=str,
    error_message=str | None,
    diversity_indices=dict(
        shannon=float,
        simpson=float,
        species_richness=int,
    ),
    composition=dict[str, float],     # percentage per class
    bloom_alerts=list[dict(
        class_name=str,
        count=int,
        threshold=int,
    )],
    trends=dict | None,               # optional time‑series metrics
)
```

**Implementation notes**

- Use counts to compute Shannon and Simpson indices and species richness for each sample.
- Bloom detection compares counts to configurable thresholds for specific classes (e.g., harmful algal taxa).

***

## Module 7 – Export \& reporting

**Responsibility**: Persist results and optionally serve a local dashboard.

**Input contract**

```python
ExportInput = dict(
    metadata=dict,
    counts_by_class=dict[str, int],
    organisms=list[dict],
    diversity_indices=dict,
    bloom_alerts=list[dict],
    export_config=dict(
        output_dir=str,
        generate_dashboard=bool,
        export_images=bool,
    ),
)
```

**Output contract**

```python
ExportOutput = dict(
    status=str,
    error_message=str | None,
    csv_path=str,
    dashboard_url=str | None,
    exported_files=list[str],
)
```

**CSV schema (row‑wise)**

```text
sample_id,timestamp,gps_lat,gps_lon,magnification,
class_name,count,mean_size_um,shannon_diversity,bloom_alert
```

**Implementation notes**

- Use CSV as the canonical interface to external tools; embed geolocation and time for downstream mapping.
- Optional Streamlit/Folium dashboard runs locally on device or laptop and reads CSVs as its data source.

***

## Shared module interface

Define a common abstract base so all modules can be orchestrated generically:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class PipelineModule(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validate_config()

    @abstractmethod
    def validate_config(self) -> None:
        ...

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> None:
        ...

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        return {
            "status": "error",
            "error_message": str(error),
            "error_type": type(error).__name__,
        }
```

This ensures each module exposes the same surface: `validate_config`, `validate_input`, `process`, and standardized error handling, which strongly supports substitutabil

***

## Pipeline manager

The manager is a thin orchestrator that wires modules together using contracts.

```python
class PipelineManager:
    def __init__(self, config: dict, modules: dict):
        self.config = config
        self.modules = modules  # dict[name -> PipelineModule]

    def execute_pipeline(self, acquisition_params: dict) -> dict:
        # 1. Acquire
        r1 = self.modules["acquisition"].process(acquisition_params)
        if r1["status"] != "success":
            return {"status": "error", "failed_at": "acquisition", **r1}

        # 2. Preprocess
        r2 = self.modules["preprocessing"].process({
            "image": r1["image"],
            "preprocessing_config": self.config["preprocessing"],
        })
        if r2["status"] != "success":
            return {"status": "error", "failed_at": "preprocessing", **r2}

        # 3. Segment
        r3 = self.modules["segmentation"].process({
            "image": r2["processed_image"],
            "segmentation_config": self.config["segmentation"],
        })
        if r3["status"] != "success":
            return {"status": "error", "failed_at": "segmentation", **r3}

        # 4. Classify
        r4 = self.modules["classification"].process({
            "image": r2["processed_image"],
            "masks": r3["masks"],
            "bounding_boxes": r3["bounding_boxes"],
            "classification_config": self.config["classification"],
        })
        if r4["status"] != "success":
            return {"status": "error", "failed_at": "classification", **r4}

        # 5. Count
        r5 = self.modules["counting"].process({
            "predictions": r4["predictions"],
            "areas_px": r3["areas_px"],
            "centroids": r3["centroids"],
            "metadata": r1["metadata"],
            "counting_config": self.config["counting"],
        })
        if r5["status"] != "success":
            return {"status": "error", "failed_at": "counting", **r5}

        # 6. Analytics
        r6 = self.modules["analytics"].process({
            "counts_by_class": r5["counts_by_class"],
            "organisms": r5["organisms"],
            "analytics_config": self.config["analytics"],
        })
        if r6["status"] != "success":
            return {"status": "error", "failed_at": "analytics", **r6}

        # 7. Export
        r7 = self.modules["export"].process({
            "metadata": r1["metadata"],
            "counts_by_class": r5["counts_by_class"],
            "organisms": r5["organisms"],
            "diversity_indices": r6["diversity_indices"],
            "bloom_alerts": r6["bloom_alerts"],
            "export_config": self.config["export"],
        })

        return {
            "status": r7["status"],
            "csv_path": r7.get("csv_path"),
            "dashboard_url": r7.get("dashboard_url"),
            "summary": {
                "total_organisms": r5["total_count"],
                "species_richness": r6["diversity_indices"]["species_richness"],
                "bloom_alerts": len(r6["bloom_alerts"]),
            },
        }
```

The manager never touches implementation details of modules; it only relies on their contracts, which is crucial for preserving modularity when swapping implementations.

***

## Config file and directory layout

### Example `config.yaml`

```yaml
pipeline:
  name: "Marine Plankton AI Microscope"
  version: "1.0.0"

acquisition:
  camera_type: "pi_hq"
  default_magnification: 2.0
  default_exposure_ms: 100
  sensor_pixel_size_um: 1.55

preprocessing:
  denoise_method: "bilateral"
  normalize: true
  background_correction: true
  flatfield_correction: false

segmentation:
  method: "watershed"
  min_area_px: 100
  max_area_px: 50000
  handle_overlaps: true

classification:
  model_path: "./models/plankton_classifier_v1.tflite"
  class_names: ["Copepod", "Diatom", "Dinoflagellate", "Ciliate", "Other"]
  confidence_threshold: 0.7
  top_k: 3

counting:
  confidence_threshold: 0.7
  size_range_um: [10, 1000]
  count_by_class: true

analytics:
  compute_diversity: true
  compute_composition: true
  bloom_thresholds:
    Dinoflagellate: 5000
    Diatom: 10000

export:
  output_dir: "./results"
  generate_dashboard: true
  export_images: true
```


### Suggested project layout

```text
project_root/
├── config/
│   ├── config.yaml
│   └── hardware_profiles/
│       ├── pi4.yaml
│       └── jetson.yaml
├── modules/
│   ├── __init__.py
│   ├── base.py            # PipelineModule
│   ├── acquisition.py
│   ├── preprocessing.py
│   ├── segmentation.py
│   ├── classification.py
│   ├── counting.py
│   ├── analytics.py
│   └── export.py
├── pipeline/
│   ├── __init__.py
│   ├── manager.py
│   └── validators.py
├── models/
├── tests/
├── utils/
├── dashboard/
├── results/
├── docs/
└── main.py
```

This directory structure mirrors the module boundaries, helping keep coupling low and cohesion high in the codeb

***
