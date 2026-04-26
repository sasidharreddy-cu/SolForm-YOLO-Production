# Solform YOLO — Colleague Setup (5 commands)

Train the form-element YOLOv8 model on Modal cloud GPUs, end-to-end.
**No GPU needed on your machine.** Everything runs on Modal's servers.

**Tested**: Windows 11, Python 3.12, Modal 1.3 — completed in ~13 minutes
on an A100 GPU and produced `best.pt` with mAP50 = 0.906.

---

## What you need before starting

| Item | How to get it |
|---|---|
| Python 3.12+ | https://www.python.org/downloads/ |
| A Modal account | https://modal.com — free, $30/month credit (training run costs ~$1–3) |
| The repo | Clone or unzip this folder somewhere local |
| The `training_data/` folder | Must contain ~1324 files (662 PNG + 662 JSON pairs). If it's not in the repo, ask the project owner for the zip and extract it into `./training_data/`. |

---

## Step 1 — One-time install (run ONCE per machine)

Open **PowerShell** (recommended on Windows — avoids Git Bash path issues) and run:

```powershell
# 1. Install Modal CLI
pip install modal

# 2. Authenticate (opens your browser to log in to Modal)
modal token new
```

✅ If `modal profile current` prints your Modal username, you're authenticated.

---

## Step 2 — Run the full training pipeline (4 commands)

From the project root (`solform-yolo-production/`):

```powershell
# 1. Create the Modal volume + directory structure
modal run setup_modal.py

# 2. Upload your local training data to the Modal volume
#    (~1300 files, takes a couple of minutes)
modal volume put solform-data ./training_data /ExportSFsPNGs --force

# 3. Train the model (runs on Modal's A100 GPU, ~15 minutes total)
modal run train_standalone.py

# 4. (Optional) Download the trained model to your machine
modal volume get solform-data /runs ./runs
```

That's it. After step 3 finishes, your trained weights live at
`/runs/forms/weights/best.pt` on the Modal volume.

While training runs, you can watch live logs at the URL printed in the
console (looks like `https://modal.com/apps/<your-username>/main/ap-...`).

---

## Step 3 — Run predictions

```powershell
# Put images you want to predict on into a local ./predict_inputs/ folder, then:
modal volume put solform-data ./predict_inputs /predict_inputs --force
modal run predict_standalone.py

# Download the annotated outputs:
modal volume get solform-data /predict_outputs ./predict_outputs
```

---

## Common gotchas (read this if something fails)

### ❌ `'charmap' codec can't encode character '✓'`
Windows console can't print Unicode. **Fix once per shell:**
```powershell
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONUTF8="1"
```
Then re-run the failing command. (PowerShell is fine; Git Bash on Windows
also needs `MSYS_NO_PATHCONV=1` — see next gotcha.)

### ❌ Files uploaded to a path like `C:/Program Files/Git/ExportSFsPNGs`
Only happens in **Git Bash** on Windows — MSYS converts `/ExportSFsPNGs`
into a Windows path. **Fix:**
```bash
export MSYS_NO_PATHCONV=1
modal volume put solform-data ./training_data /ExportSFsPNGs --force
```
Or just use **PowerShell** instead — it has no path mangling.

If you already uploaded to the wrong path, clean it up:
```powershell
modal volume rm solform-data "C:/Program Files/Git/ExportSFsPNGs" -r
```

### ❌ Training "hangs" with no output for 5+ minutes after `Created function train.`
**This is normal on the very first run.** Modal is building the container
image (downloads PyTorch ~2 GB, ultralytics, opencv). One-time only — every
later run starts in seconds.

You can confirm by opening the dashboard URL printed in the console.

### ❌ `Volume not found` or training script can't find data
Check the volume contents:
```powershell
modal volume ls solform-data /
modal volume ls solform-data /ExportSFsPNGs
```
You should see ~1324 files in `/ExportSFsPNGs`. If not, re-run step 2 of the
upload, making sure you're in the project root and `./training_data/` exists
locally.

### ❌ B200 GPU queued forever
B200 is the newest GPU and often has long queues. **Already fixed** in
`train_standalone.py` — it uses **A100** (line 56). If you want to change it,
edit that line. Options: `T4`, `A10G`, `A100`, `B200`. A10G needs `batch=16`
(line 48) to fit 24 GB VRAM; A100/B200 can use `batch=32`.

### ❌ Out of GPU memory
Lower the batch size in `train_standalone.py` line 48:
```python
"batch": 16,   # or 8 if still OOM
```

---

## Cost estimate (Modal billing)

| Step | GPU | Time | Approx cost |
|---|---|---|---|
| First-time image build | none | ~10 min | ~$0.05 |
| Training (50 epochs, 662 images) | A100 | ~13 min | ~$2 |
| Each prediction batch (100 imgs) | A100 | ~1 min | ~$0.20 |

Modal gives **$30/month free credit**. One full train + predict cycle is
well under $5.

---

## Reset everything (if you want to start fresh)

```powershell
modal run cleanup_modal.py        # wipes the volume contents
```

Or to delete and recreate the entire volume:
```powershell
modal volume delete solform-data
modal run setup_modal.py
```
