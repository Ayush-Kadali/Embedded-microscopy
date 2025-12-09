# Dashboard Quick Start Guide

## 🚀 Launch Dashboard

```bash
# From project root directory
source .venv/bin/activate
streamlit run dashboard/app.py
```

**Access URL**: http://localhost:8501

---

## 📸 Three Steps to Analysis

### Step 1: Capture Image
- **Option A**: Click camera icon → Take photo
- **Option B**: Click "Browse files" → Upload image

### Step 2: Set Location (Optional)
- Enter sample location in sidebar
- Example: "Mumbai Coast", "Bay of Bengal"

### Step 3: Analyze
- Click **"Run Analysis"** button
- Wait 10-20 seconds
- View results in "Results" tab

---

## 📊 Reading Results

### Key Metrics
- **Total Organisms**: Number detected
- **Species Detected**: Unique species count
- **Shannon Diversity**: 0-3 scale (higher = more diverse)
- **Simpson Diversity**: 0-1 scale (higher = more diverse)

### Charts

**Species Distribution (Pie Chart)**
- Shows percentage of each species
- Hover for exact counts

**Size Distribution (Histogram)**
- Organism size distribution
- Red line = average size

**Confidence Scores (Bar Chart)**
- AI confidence for each organism
- Green (>70%) = reliable
- Yellow (50-70%) = moderate
- Red (<50%) = needs verification

**Annotated Image**
- Organisms highlighted with boxes
- Labels show species + confidence

---

## 💾 Export Results

Click download buttons for:
- **Summary CSV**: Overall statistics
- **Organisms CSV**: Individual organism data
- **JSON**: Complete results

---

## ⚠️ Bloom Detection

**Green** ✅: No bloom (healthy ecosystem)
**Yellow** ⚠️: Bloom detected (shows dominant species + %)

Bloom = >50% of single species

---

## 🎯 Best Practices

### Image Quality
✅ **Good**: Sharp focus, even lighting, clear background
❌ **Bad**: Blurry, dark/bright spots, cluttered

### Confidence Levels
- **>70%**: Trust the prediction
- **50-70%**: Probably correct
- **<50%**: Manually verify

### Sample Preparation
- Use 100-400x magnification
- Dilute if organisms overlap
- Remove large debris

---

## 🔬 19 Species Recognized

**Diatoms**: Asterionellopsis glacialis, Cerataulina, Chaetoceros, Entomoneis, Guinardia, Hemiaulus, Lauderia annulata, Nitzschia, Pinnularia, Pleurosigma, Thalassionema, Thalassiosira

**Dinoflagellates**: Alexandrium, Ceratium, Noctiluca, Ornithocercus magnificus, Prorocentrum, Protoperidinium, Pyrodinium

---

## ❓ Common Issues

**No organisms detected?**
- Check focus and lighting
- Ensure 100-400x magnification
- Increase sample concentration

**Low confidence scores?**
- Improve image quality (focus, lighting)
- Species might not be in training set
- Recapture with better settings

**Camera not working?**
- Grant browser camera permission
- Close other apps using camera
- Try Chrome/Firefox instead of Safari
- Use file upload as alternative

---

## 📞 Quick Help

- **Full Guide**: `DASHBOARD_GUIDE.md`
- **Model Performance**: `EVALUATION_REPORT.md`
- **Setup Info**: `SETUP_COMPLETE.md`

---

## 🎯 Model Stats

- **Accuracy**: 83.48%
- **Best Species**: Noctiluca (96.8%), Asterionellopsis (96.7%)
- **Average Confidence**: 75-90%

---

**Ready to analyze plankton! 🔬**

Open http://localhost:8501 in your browser.
