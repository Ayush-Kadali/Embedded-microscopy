# EcoTaxa Complete Workflow Guide

This document provides a step-by-step guide to using EcoTaxa for plankton classification.

---

## 🌐 Web Interface Workflow

### Step 1: Account Creation

1. Visit https://ecotaxa.obs-vlfr.fr/
2. Click **"Sign Up"** or **"Register"**
3. Fill in registration form:
   - Username
   - Email
   - Password
   - Affiliation (your institution)
4. Check email for verification link
5. Log in with credentials

### Step 2: Create a Project

1. **Navigate to Projects**:
   - Click "My Projects" or "Create Project"

2. **Project Setup**:
   - **Title**: e.g., "SIH 2025 - Marine Plankton Field Samples"
   - **Description**: Project details, sampling location, methodology
   - **Visibility**: Private (for testing) or Public
   - **Instrument**: Select imaging device (or create custom)
   - **Contact**: Your contact information

3. **Configure Project Settings**:
   - Set default classification categories
   - Configure user permissions
   - Set up sampling metadata fields

### Step 3: Upload Images

#### Option A: Single Image Upload
1. Go to your project
2. Click **"Import"** or **"Add Images"**
3. Select image file from computer
4. Fill in metadata:
   - Sample ID
   - Date/Time
   - GPS coordinates (lat/lon)
   - Depth
   - Temperature
   - Other environmental data

#### Option B: Batch Upload (Recommended)
1. **Prepare TSV File** (Tab-Separated Values):
   ```tsv
   img_file_name	object_id	sample_id	object_date	object_time	object_lat	object_lon	object_depth_min	object_depth_max
   plankton_001.jpg	1	SAMPLE_001	20251208	120000	18.5204	73.8567	5	10
   plankton_002.jpg	2	SAMPLE_001	20251208	120030	18.5204	73.8567	5	10
   ```

2. **Prepare Image ZIP**:
   - Create a ZIP file with all images
   - Image names must match `img_file_name` in TSV

3. **Upload**:
   - Go to project → Import → "General"
   - Upload TSV file
   - Upload ZIP file with images
   - Click "Preview" to validate
   - Click "Import" to process

### Step 4: ML-Assisted Classification

1. **Trigger Prediction**:
   - Go to project → "Classification" tab
   - Click **"Predict"** or **"Auto-classify"**
   - Select ML model (if multiple available)
   - Set confidence threshold (e.g., 0.7)
   - Click "Start Prediction"

2. **Monitor Job**:
   - Go to "Jobs" tab
   - Check prediction status
   - Wait for completion (can take minutes to hours depending on image count)

3. **Review Predictions**:
   - Go to "Objects" tab
   - Filter by "Predicted" status
   - View predicted class and confidence score
   - Images sorted by confidence (review low-confidence first)

### Step 5: Manual Validation

1. **Review Interface**:
   - Click on an object to enlarge
   - View predicted class and confidence
   - View similar objects (visual similarity search)

2. **Validation Options**:
   - **Accept**: Click checkmark (object marked as validated)
   - **Change Class**: Select correct class from dropdown
   - **Skip**: Move to next object
   - **Flag**: Mark as problematic for expert review

3. **Keyboard Shortcuts** (faster annotation):
   - Arrow keys: Navigate between objects
   - Number keys: Quick class selection
   - Enter: Validate current prediction
   - Space: Next object

### Step 6: Export Results

1. **Navigate to Export**:
   - Go to project → "Export" tab

2. **Export Options**:

   **A. Summary Export** (counts by class):
   ```csv
   sample_id,class_name,count,date,location
   SAMPLE_001,Copepod,23,2025-12-08,18.5204_73.8567
   SAMPLE_001,Diatom,45,2025-12-08,18.5204_73.8567
   ```

   **B. Detailed Export** (per-object data):
   ```csv
   object_id,sample_id,class_name,confidence,area_px,date,lat,lon
   1,SAMPLE_001,Copepod,0.87,1523,2025-12-08,18.5204,73.8567
   2,SAMPLE_001,Diatom,0.92,2341,2025-12-08,18.5204,73.8567
   ```

   **C. Images Export**:
   - Download original images
   - Download thumbnails
   - Include or exclude unvalidated objects

3. **Choose Format**:
   - CSV/TSV: For spreadsheet analysis
   - DarwinCore: For biodiversity databases
   - JSON: For programmatic processing

4. **Download**:
   - Click "Export"
   - Job created in background
   - Download link appears when ready
   - Files saved as ZIP

---

## 🐍 Python API Workflow

### Prerequisites

```bash
# Install Python client
pip install git+https://github.com/ecotaxa/ecotaxa_py_client.git

# Install supporting libraries
pip install pandas pillow
```

### Step 1: Authentication

```python
import ecotaxa_py_client
from ecotaxa_py_client.api import authentification_api
from ecotaxa_py_client.model.login_req import LoginReq

# Configure API client
configuration = ecotaxa_py_client.Configuration(
    host="https://ecotaxa.obs-vlfr.fr/api"
)

# Create API client
with ecotaxa_py_client.ApiClient(configuration) as api_client:
    # Create authentication API instance
    auth_api = authentification_api.AuthentificationApi(api_client)

    # Login
    login_req = LoginReq(
        username="your_username",
        password="your_password"
    )

    # Get access token
    token_response = auth_api.login(login_req)
    access_token = token_response['token']

    print(f"Logged in successfully! Token: {access_token[:20]}...")
```

### Step 2: Create Project

```python
from ecotaxa_py_client.api import projects_api
from ecotaxa_py_client.model.create_project_req import CreateProjectReq

# Configure with access token
configuration.access_token = access_token

with ecotaxa_py_client.ApiClient(configuration) as api_client:
    projects_api_instance = projects_api.ProjectsApi(api_client)

    # Create project
    project_req = CreateProjectReq(
        title="SIH 2025 Automated Field Samples"
    )

    project_id = projects_api_instance.create_project(project_req)
    print(f"Project created with ID: {project_id}")
```

### Step 3: Upload Images

```python
from ecotaxa_py_client.api import files_api
import os

files_api_instance = files_api.FilesApi(api_client)

# Upload single image
image_path = "test_images/plankton_001.jpg"
with open(image_path, 'rb') as image_file:
    upload_response = files_api_instance.upload_file(
        project_id=project_id,
        file=image_file
    )
    print(f"Image uploaded: {upload_response}")
```

### Step 4: Import to Project

```python
from ecotaxa_py_client.api import objects_api
import pandas as pd

# Prepare metadata TSV
metadata = pd.DataFrame({
    'img_file_name': ['plankton_001.jpg'],
    'object_id': [1],
    'sample_id': ['SAMPLE_001'],
    'object_date': ['20251208'],
    'object_time': ['120000'],
    'object_lat': [18.5204],
    'object_lon': [73.8567],
    'object_depth_min': [5],
    'object_depth_max': [10]
})

# Save TSV
tsv_path = 'metadata.tsv'
metadata.to_csv(tsv_path, sep='\t', index=False)

# Upload TSV
with open(tsv_path, 'rb') as tsv_file:
    tsv_response = files_api_instance.upload_file(
        project_id=project_id,
        file=tsv_file
    )

# Trigger import job
# (Requires JobsApi - see API docs for details)
```

### Step 5: Get Classifications

```python
from ecotaxa_py_client.api import objects_api

objects_api_instance = objects_api.ObjectsApi(api_client)

# Query objects in project
object_set = objects_api_instance.get_object_set(
    project_id=project_id,
    # Optional filters
    # status_filter='V',  # Validated only
    # taxon_ids=[123, 456],  # Specific taxa
)

# Process results
for obj in object_set['objects']:
    print(f"Object ID: {obj['objid']}")
    print(f"Class: {obj['classif_auto_name']}")
    print(f"Confidence: {obj['classif_auto_score']}")
    print(f"Validated Class: {obj.get('classif_name', 'Not validated')}")
    print("---")
```

### Step 6: Export Data

```python
from ecotaxa_py_client.api import projects_api

# Export summary
export_response = projects_api_instance.project_export(
    project_id=project_id,
    export_type='summary'  # or 'detail', 'backup'
)

# Download export file
job_id = export_response['job_id']

# Monitor job status
from ecotaxa_py_client.api import jobs_api
jobs_api_instance = jobs_api.JobsApi(api_client)

job_status = jobs_api_instance.get_job(job_id)
while job_status['state'] != 'F':  # F = Finished
    time.sleep(5)
    job_status = jobs_api_instance.get_job(job_id)

# Get download link
download_url = job_status.get('result', {}).get('url')
print(f"Download export from: {download_url}")
```

---

## 🔄 Complete Automation Script

Here's a complete script that automates the entire workflow:

```python
#!/usr/bin/env python3
"""
Complete EcoTaxa Workflow Automation
Upload images → Predict → Export results
"""

import ecotaxa_py_client
from ecotaxa_py_client.api import (
    authentification_api,
    projects_api,
    files_api,
    objects_api,
    jobs_api
)
from ecotaxa_py_client.model.login_req import LoginReq
from ecotaxa_py_client.model.create_project_req import CreateProjectReq
import time
import os
from pathlib import Path

class EcoTaxaWorkflow:
    def __init__(self, username, password):
        self.configuration = ecotaxa_py_client.Configuration(
            host="https://ecotaxa.obs-vlfr.fr/api"
        )
        self.username = username
        self.password = password
        self.access_token = None
        self.project_id = None

    def authenticate(self):
        """Step 1: Login and get access token"""
        with ecotaxa_py_client.ApiClient(self.configuration) as api_client:
            auth_api = authentification_api.AuthentificationApi(api_client)
            login_req = LoginReq(
                username=self.username,
                password=self.password
            )
            response = auth_api.login(login_req)
            self.access_token = response['token']
            self.configuration.access_token = self.access_token
            print("✓ Authenticated successfully")

    def create_project(self, title):
        """Step 2: Create new project"""
        with ecotaxa_py_client.ApiClient(self.configuration) as api_client:
            proj_api = projects_api.ProjectsApi(api_client)
            project_req = CreateProjectReq(title=title)
            self.project_id = proj_api.create_project(project_req)
            print(f"✓ Project created: ID {self.project_id}")

    def upload_images(self, image_dir):
        """Step 3: Upload all images from directory"""
        with ecotaxa_py_client.ApiClient(self.configuration) as api_client:
            files_api_instance = files_api.FilesApi(api_client)

            image_dir = Path(image_dir)
            images = list(image_dir.glob('*.jpg')) + list(image_dir.glob('*.png'))

            print(f"Uploading {len(images)} images...")
            for img_path in images:
                with open(img_path, 'rb') as img_file:
                    files_api_instance.upload_file(
                        project_id=self.project_id,
                        file=img_file
                    )
                print(f"  ✓ Uploaded {img_path.name}")

    def get_results(self):
        """Step 4: Get classification results"""
        with ecotaxa_py_client.ApiClient(self.configuration) as api_client:
            obj_api = objects_api.ObjectsApi(api_client)

            object_set = obj_api.get_object_set(
                project_id=self.project_id
            )

            results = []
            for obj in object_set.get('objects', []):
                results.append({
                    'object_id': obj['objid'],
                    'predicted_class': obj.get('classif_auto_name', 'Unknown'),
                    'confidence': obj.get('classif_auto_score', 0.0),
                    'validated_class': obj.get('classif_name', None)
                })

            print(f"✓ Retrieved {len(results)} results")
            return results

    def export_project(self):
        """Step 5: Export project data"""
        with ecotaxa_py_client.ApiClient(self.configuration) as api_client:
            proj_api = projects_api.ProjectsApi(api_client)
            jobs_api_instance = jobs_api.JobsApi(api_client)

            # Start export job
            export_response = proj_api.project_export(
                project_id=self.project_id,
                export_type='detail'
            )
            job_id = export_response['job_id']
            print(f"✓ Export job started: {job_id}")

            # Wait for completion
            while True:
                job_status = jobs_api_instance.get_job(job_id)
                state = job_status['state']

                if state == 'F':  # Finished
                    download_url = job_status['result']['url']
                    print(f"✓ Export complete: {download_url}")
                    return download_url
                elif state == 'E':  # Error
                    print("✗ Export failed")
                    return None

                time.sleep(5)

# Usage
if __name__ == "__main__":
    workflow = EcoTaxaWorkflow(
        username="your_username",
        password="your_password"
    )

    workflow.authenticate()
    workflow.create_project("Test Project")
    workflow.upload_images("./test_images")
    results = workflow.get_results()
    export_url = workflow.export_project()

    print("\n=== Results Summary ===")
    for result in results:
        print(f"{result['predicted_class']}: {result['confidence']:.2f}")
```

---

## 📊 Understanding EcoTaxa Results

### Confidence Scores
- **0.9-1.0**: Very confident - likely correct
- **0.7-0.9**: Confident - usually correct, review recommended
- **0.5-0.7**: Moderate - human review needed
- **0.0-0.5**: Low confidence - manual classification required

### Classification Status
- **P**: Predicted (by ML, not validated)
- **V**: Validated (human-verified)
- **D**: Dubious (flagged for expert review)
- **U**: Unclassified (no prediction yet)

### Taxonomic Hierarchy
EcoTaxa uses standard taxonomic ranks:
- Kingdom → Phylum → Class → Order → Family → Genus → Species

Predictions can be at any rank level.

---

## 🎯 Tips for Best Results

### Image Quality
- **Resolution**: Minimum 640x640px recommended
- **Focus**: Sharp, clear images
- **Lighting**: Consistent, even illumination
- **Background**: Clean, minimal debris
- **Orientation**: Consistent (top-down view)

### Metadata Importance
- **GPS**: Accurate coordinates help with species distribution
- **Date/Time**: Important for temporal analysis
- **Depth**: Critical for habitat association
- **Temperature**: Affects species presence

### Validation Strategy
1. **Start with high-confidence** predictions (>0.9)
2. **Batch validate** if predictions look correct
3. **Focus on low-confidence** items (<0.7)
4. **Use visual similarity** to find examples
5. **Consult experts** for difficult cases

---

## ⚠️ Common Issues & Solutions

### Issue 1: Upload Fails
**Cause**: Image format or size
**Solution**:
- Convert to JPEG or PNG
- Resize if >10MB
- Check file name (no special characters)

### Issue 2: No Predictions
**Cause**: Model not available or images too poor quality
**Solution**:
- Check image quality
- Request model access (if using specialized models)
- Try manual classification first

### Issue 3: API Authentication Fails
**Cause**: Token expired or incorrect credentials
**Solution**:
- Re-login to get new token
- Check username/password
- Ensure API access is enabled for your account

### Issue 4: Slow Processing
**Cause**: Large batch or server load
**Solution**:
- Upload in smaller batches (50-100 images)
- Process during off-peak hours
- Use async job monitoring

---

## 📚 Additional Resources

- **Video Tutorials**: Check EcoTaxa YouTube channel (if available)
- **User Manual**: https://ecotaxa.obs-vlfr.fr/docs
- **API Examples**: https://github.com/ecotaxa/ecotaxa_py_client/tree/main/examples
- **Community Forum**: Ask questions on GitHub issues

---

**Next**: See `INTEGRATION_OPTIONS.md` for how to integrate this into our prototype
