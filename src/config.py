import os
from pathlib import Path

# --- CHEMINS DU PROJET ---
SRC_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SRC_DIR.parent
PROJECT_ROOT = PROJECT_DIR  # Résout l'erreur PROJECT_ROOT

DATA_DIR = PROJECT_DIR / "data"
MODELS_DIR = PROJECT_DIR / "models"
RESULTS_DIR = PROJECT_DIR / "results"
PLOTS_DIR = PROJECT_DIR / "plots"
LOGS_DIR = PROJECT_DIR / "logs"

# --- FICHIERS DE SORTIE (Résout l'erreur MODEL_METRICS_FILE) ---
MODEL_METRICS_FILE = RESULTS_DIR / "model_metrics.csv"

# --- CONFIGURATION STREAMLIT & RÉSEAU ---
APP_ENTRYPOINT = SRC_DIR / "app.py"
STREAMLIT_HOST = "localhost"
STREAMLIT_PORT = 8501

# --- CONFIGURATION DE L'ENVIRONNEMENT ---
ENV_FILE = PROJECT_DIR / ".env"

# --- REGISTRE DES MODÈLES ENTRAÎNÉS ---
MODELS = {
    "ridge": {
        "name": "Régression Ridge (Expert)",
        "description": "Modèle linéaire avec régularisation L2 et Standard Scaling intégré.",
        "path": MODELS_DIR / "ridge_expert_model.joblib",
    },
    "rf": {
        "name": "Random Forest (Expert)",
        "description": "Ensemble d'arbres de décision optimisé pour capturer les non-linéarités.",
        "path": MODELS_DIR / "random_forest_expert_model.joblib",
    },
    "gb": {
        "name": "Gradient Boosting (Expert)",
        "description": "Modèle de boosting séquentiel offrant d'excellentes performances prédictives.",
        "path": MODELS_DIR / "gradient_boosting_expert_model.joblib",
    }
}