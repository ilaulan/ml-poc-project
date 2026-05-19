from typing import Any
from sklearn.metrics import mean_absolute_error, r2_score

def compute_metrics(y_true: Any, y_pred: Any) -> dict[str, float]:
    """
    Calcule les métriques d'évaluation pour les modèles de régression du taux de retard.
    """
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    return {
        "MAE": float(mae),
        "R2_Score": float(r2)
    }