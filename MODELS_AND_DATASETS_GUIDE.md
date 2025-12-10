# 🤖 Models & Datasets - Quick Reference

## ✅ **Your Custom Plankton Model**: best.pt

### Location
```
Downloaded models/best.pt
```

### Detects 6 Algal Plankton Species:
1. **Platymonas**
2. **Chlorella**
3. **Dunaliella salina**
4. **Effrenium**
5. **Porphyridium**
6. **Haematococcus**

### ✅ Use This For:
- Algal plankton detection
- Real-time video analysis
- Aquaculture monitoring
- Bloom detection
- Fast screening

### ❌ NOT For:
- Diatoms (use MobileNetV2)
- Dinoflagellates (use MobileNetV2)
- Generic objects

---

## 📊 Other Models

### MobileNetV2 & EfficientNet
- **Species**: 19 marine plankton (diatoms/dinoflagellates)
- **Use for**: Marine biodiversity, ocean monitoring
- **NOT for**: The 6 algal species above

---

## 🎯 Quick Decision

**Detecting algae?** → Use **best.pt** (YOLO)
**Detecting diatoms/dinoflagellates?** → Use MobileNetV2/EfficientNet
**Video analysis?** → Use **best.pt** (YOLO)

---

## ✅ System Now Configured

All dashboards now:
- **Prioritize best.pt** (your custom model)
- **Warn if wrong model selected**
- **Show which species each model detects**
- **Auto-select best.pt by default**

Just run: `./run_live_demo.sh` or `./run_dashboard.sh`
