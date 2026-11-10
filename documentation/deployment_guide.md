# GlucoShield CDSS — Deployment & Operations Guide

**FUSE AI-201 Capstone | Module 6: Deployment Documentation**  
**Project:** GlucoShield Diabetic Readmission CDSS  
**Group:** Group 04 (YEEAP Capstone)  

---

> [!NOTE]
> **Deployment Status Declaration:**  
> GlucoShield is currently validated as a **fully functional local clinical decision support prototype** and containerized service. Cloud deployment instructions for Streamlit Community Cloud and Docker are provided below as verified deployment procedures. No public production cloud URL is claimed unless independently hosted and verified.

---

## 1. Local Environment Setup & Execution

### Prerequisites
- Python 3.10, 3.11, or 3.12+ (tested and verified on Python 3.15.2)
- Git & pip

### Step 1: Clone and Prepare Environment
```bash
git clone https://github.com/biluyb/diabetic-hospital-readmission-risk-predictor.git
cd diabetic-hospital-readmission-risk-predictor

# Create virtual environment (recommended)
python -m venv .venv

# Activate environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate
```

### Step 2: Install Verified Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Run Full Pipeline (Optional Verification)
To verify end-to-end data cleaning, training, testing, and drift evaluation:
```bash
python run_full_pipeline.py
```

### Step 4: Launch the Streamlit Interactive Dashboard
```bash
streamlit run app.py
```
Open your browser at **http://localhost:8501** to interact with the CDSS dashboard.

---

## 2. Running the FastAPI REST Microservice

For machine-to-machine integrations (e.g., electronic medical record systems sending JSON payloads):

### Launch the API Server
```bash
uvicorn src.api:api_app --host 0.0.0.0 --port 8000 --reload
```

### Interactive API Documentation
Open your browser at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Test Endpoints via cURL or PowerShell

**1. Health Check:**
```bash
curl -X GET "http://localhost:8000/health"
```
*Expected Response:*
```json
{
  "status": "HEALTHY",
  "service": "GlucoShield CDSS API",
  "model_status": "READY",
  "selected_model": "XGBoost Classifier",
  "decision_threshold": 0.45
}
```

**2. Patient Readmission Prediction:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "race": "Caucasian",
    "gender": "Female",
    "age": "[70-80)",
    "time_in_hospital": 6,
    "num_lab_procedures": 58,
    "num_procedures": 2,
    "num_medications": 22,
    "number_outpatient": 1,
    "number_emergency": 1,
    "number_inpatient": 3,
    "number_diagnoses": 9,
    "diag_1": "428",
    "insulin": "Up",
    "change": "Ch",
    "diabetesMed": "Yes"
  }'
```
*Expected Response:*
```json
{
  "status": "SUCCESS",
  "probability": 0.7271,
  "decision_threshold": 0.45,
  "is_readmission_predicted": true,
  "risk_tier": "HIGH RISK",
  "action_summary": "Proactive intensive transition protocol recommended.",
  "warnings": []
}
```

---

## 3. Docker Container Deployment

The repository includes a production-ready `Dockerfile` and `.dockerignore`.

### Build Container Image
```bash
docker build -t glucoshield-cdss:v1.0 .
```

### Run Container Locally
```bash
docker run -d --name glucoshield-app -p 8501:8501 -p 8000:8000 glucoshield-cdss:v1.0
```
- Access Streamlit UI at `http://localhost:8501`
- Verify container health: `docker ps`

---

## 4. Streamlit Community Cloud Deployment

To deploy GlucoShield for online demonstration via Streamlit Community Cloud:

1. **Push Repository to GitHub:** Ensure all code, `models/`, `plots/`, and `requirements.txt` are pushed to your GitHub repository:
   ```bash
   git push origin master
   ```
2. **Access Streamlit Community Cloud:**
   - Log in at [share.streamlit.io](https://share.streamlit.io).
   - Click **"New app"**.
3. **Configure App Settings:**
   - **Repository:** `biluyb/diabetic-hospital-readmission-risk-predictor`
   - **Branch:** `master`
   - **Main file path:** `app.py`
4. **Deploy:** Click **"Deploy!"**. Streamlit will install dependencies from `requirements.txt` and launch the web interface.

