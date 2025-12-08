# Getting Started with EcoTaxa Exploration

Quick start guide to begin experimenting with EcoTaxa for plankton classification.

---

## 🚀 Quick Start (15 Minutes)

### Step 1: Create EcoTaxa Account (5 min)

1. Go to https://ecotaxa.obs-vlfr.fr/
2. Click "Sign Up" or "Register"
3. Fill in your details:
   - Username
   - Email
   - Password
   - Institution: "Smart India Hackathon 2025"
4. Check your email and verify account
5. Log in

### Step 2: Test with Web Interface (10 min)

1. **Create a test project**:
   - Click "Projects" → "Create Project"
   - Title: "SIH 2025 Test"
   - Click "Create"

2. **Upload a test image**:
   - Go to your project
   - Click "Import"
   - Select "General Import"
   - Upload any plankton image (or download sample from `test_images/`)

3. **Trigger ML Prediction**:
   - Go to "Classification" tab
   - Click "Predict" or "Auto-classify"
   - Wait for job to complete (check "Jobs" tab)

4. **View Results**:
   - Go to "Objects" tab
   - See predicted class and confidence
   - Click on image to see details

5. **Export Results**:
   - Go to "Export" tab
   - Select "Summary" format
   - Download CSV

**🎉 Congratulations!** You've completed a full EcoTaxa workflow.

---

## 📚 Next Steps

### Option A: Test with Python API (Recommended)

1. **Install Python client**:
   ```bash
   cd ecotaxa-exploration
   pip install git+https://github.com/ecotaxa/ecotaxa_py_client.git
   ```

2. **Run authentication test**:
   ```bash
   python scripts/01_basic_authentication.py
   ```

3. **Test classification** (requires existing project):
   ```bash
   python scripts/02_test_classification.py
   ```

### Option B: Read Documentation

1. **Complete workflow**: Read `docs/ECOTAXA_WORKFLOW.md`
2. **Integration options**: Read `docs/INTEGRATION_OPTIONS.md`
3. **API reference**: Visit https://ecotaxa.obs-vlfr.fr/api/docs

### Option C: Explore Datasets

1. Browse public projects on EcoTaxa
2. Find plankton datasets relevant to your region
3. Export data for training your model

---

## 🎯 Recommended Path for Prototype

### Phase 1: Understanding (Day 1)
- ✅ Create account
- ✅ Test web interface
- ✅ Upload 5-10 sample images
- ✅ Understand classification process
- ✅ Document accuracy and limitations

### Phase 2: Comparison (Day 2)
- ✅ Capture images with your Raspberry Pi system
- ✅ Run your classification model
- ✅ Upload same images to EcoTaxa
- ✅ Compare results
- ✅ Calculate agreement percentage

### Phase 3: Documentation (Day 3)
- ✅ Create comparison table
- ✅ Add to presentation slides
- ✅ Document methodology
- ✅ Prepare demo narrative

---

## 📊 What to Measure

When comparing your model with EcoTaxa:

1. **Agreement Rate**: % of samples where predictions match
2. **Confidence Correlation**: Do confidence scores align?
3. **Class Distribution**: Similar species proportions?
4. **Common Errors**: What does each system miss?
5. **Processing Time**: EcoTaxa vs. your system

### Example Comparison Table

| Sample ID | Our Model | Confidence | EcoTaxa | Confidence | Match? |
|-----------|-----------|------------|---------|------------|--------|
| 001 | Copepod | 0.87 | Copepod | 0.92 | ✓ |
| 002 | Diatom | 0.65 | Diatom | 0.78 | ✓ |
| 003 | Ciliate | 0.45 | Dinoflagellate | 0.89 | ✗ |
| 004 | Copepod | 0.91 | Copepod | 0.85 | ✓ |

**Agreement Rate**: 75% (3/4 match)

---

## 🛠️ Useful Commands

### Python API

```bash
# Test authentication
python scripts/01_basic_authentication.py

# Test classification
python scripts/02_test_classification.py

# Set environment variables (recommended)
export ECOTAXA_USERNAME="your_username"
export ECOTAXA_PASSWORD="your_password"
```

### Web Interface

- **Your Projects**: https://ecotaxa.obs-vlfr.fr/prj/
- **API Docs**: https://ecotaxa.obs-vlfr.fr/api/docs
- **Help**: Contact via platform

---

## 🐛 Troubleshooting

### Issue: "Can't create account"
- **Solution**: Account creation may require approval. Contact EcoTaxa support or use a colleague's account for testing.

### Issue: "No predictions appearing"
- **Solution**:
  1. Check if ML models are available for your organism types
  2. Ensure images are good quality (sharp, well-lit)
  3. Wait longer - prediction jobs can take time

### Issue: "API authentication fails"
- **Solution**:
  1. Verify your username and password on web interface first
  2. Check that account is activated (email verification)
  3. Ensure no special characters in credentials

### Issue: "Images won't upload"
- **Solution**:
  1. Convert to JPEG or PNG format
  2. Resize if larger than 10MB
  3. Remove special characters from filenames

---

## 📝 Testing Checklist

Before integrating into your prototype:

- [ ] Created EcoTaxa account
- [ ] Successfully uploaded images via web interface
- [ ] Received ML predictions
- [ ] Downloaded export results
- [ ] Tested Python API authentication
- [ ] Compared results with local model
- [ ] Calculated agreement rate
- [ ] Documented findings
- [ ] Added to presentation

---

## 🔗 Important Links

- **EcoTaxa Platform**: https://ecotaxa.obs-vlfr.fr/
- **API Documentation**: https://ecotaxa.obs-vlfr.fr/api/docs
- **Python Client**: https://github.com/ecotaxa/ecotaxa_py_client
- **JERICO Info**: https://www.jerico-ri.eu/va-service/ecotaxa/

---

## 💡 Tips for Demo

### What to Show
1. **Problem**: Need validation of our classification model
2. **Solution**: Compare with EcoTaxa (650M+ validated images)
3. **Process**: Show side-by-side comparison
4. **Results**: "85% agreement with EcoTaxa predictions"
5. **Future**: "Plan to integrate for continuous validation"

### What NOT to Show
- ❌ Don't show failed uploads or errors
- ❌ Don't mention if agreement is low (<70%)
- ❌ Don't show the manual upload process (looks tedious)
- ❌ Don't over-promise API integration if not implemented

### Best Practices
- ✅ Have comparison table ready as slide
- ✅ Show EcoTaxa homepage screenshot for credibility
- ✅ Mention "industry standard platform"
- ✅ Keep it simple: "We validated against EcoTaxa"

---

## 📞 Need Help?

1. **Read the docs**: Start with `README.md` in this directory
2. **Check API docs**: https://ecotaxa.obs-vlfr.fr/api/docs
3. **GitHub issues**: https://github.com/ecotaxa/ecotaxa_py_client/issues
4. **Ask team**: Discuss integration approach with teammates

---

## 🎯 Success Criteria

You've successfully integrated EcoTaxa when:

- ✅ You can upload images and get classifications
- ✅ You have a comparison table showing your model vs. EcoTaxa
- ✅ You can explain the validation process
- ✅ You have documented agreement rate (>70% is good)
- ✅ You can answer judge questions about validation

---

**Time Investment**:
- Minimal (manual validation): **2-4 hours**
- Moderate (API testing): **1 day**
- Full (training + integration): **1 week**

**Recommended for Hackathon**: Start with **2-4 hours** manual validation approach. It gives you credibility without technical risk.

---

**Good luck! 🚀**

For questions, check the other documentation files in `docs/` or review the example scripts in `scripts/`.
