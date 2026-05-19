from typing import Any
import pandas as pd
import joblib
from config import DATA_DIR, MODELS_DIR

def load_dataset_split() -> tuple[Any, Any, Any, Any]:
    """
    Charge le dataset traité, recrée dynamiquement la baseline historique par ligne,
    et aligne strictement les features avec celles attendues par les modèles experts.
    """
    path_dataset = DATA_DIR / "processed_dataset.csv"
    if not path_dataset.exists():
        raise FileNotFoundError(f"Le fichier {path_dataset} est introuvable dans data/.")

    df = pd.read_csv(path_dataset)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date').fillna(0)

    # 1. RECRÉATION DE LA BASELINE HISTORIQUE (Résout le KeyError)
    # D'après tes notebooks, la baseline est la moyenne cumulée ou globale du taux de retard par ligne (id_ligne)
    if 'baseline_historique_ligne' not in df.columns and 'id_ligne' in df.columns:
        # On calcule la moyenne du taux de retard par ligne sur la période d'entraînement (avant 2023)
        # pour éviter le data leakage, puis on la mappe sur tout le dataset
        train_mask = df['Date'].dt.year < 2023
        baseline_map = df[train_mask].groupby('id_ligne')['target'].mean().to_dict()
        
        # Si une ligne n'existait pas dans le train, on met la moyenne globale
        global_mean = df[train_mask]['target'].mean() if train_mask.sum() > 0 else 0
        
        df['baseline_historique_ligne'] = df['id_ligne'].map(baseline_map).fillna(global_mean)

    # 2. Récupérer l'ordre et le nom exact des features depuis ton modèle Ridge
    path_modele_temoin = MODELS_DIR / "ridge_expert_model.joblib"
    if not path_modele_temoin.exists():
        raise FileNotFoundError(f"Le modèle témoin est introuvable dans {path_modele_temoin}.")
    
    modele_temoin = joblib.load(path_modele_temoin)
    features_attendues = list(modele_temoin.feature_names_in_)

    # 3. Split temporel strict (Train avant 2023 / Test en 2023)
    df_train = df[df['Date'].dt.year < 2023].copy()
    df_test = df[df['Date'].dt.year == 2023].copy()

    # 4. Extraction de la cible (target)
    y_train = df_train['target']
    y_test = df_test['target']

    # 5. Extraction et alignement des features
    # Maintenant que 'baseline_historique_ligne' est créée, l'indexation va fonctionner parfaitement !
    X_train = df_train[features_attendues]
    X_test = df_test[features_attendues]

    return X_train, X_test, y_train, y_test