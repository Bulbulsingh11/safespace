"""
analyzer.py — Toxicity Detection Engine
Uses Detoxify with full sub-label scores for detailed analysis.
"""
from __future__ import annotations

import pandas as pd
from detoxify import Detoxify

_model: Detoxify | None = None


def _get_model() -> Detoxify:
    global _model
    if _model is None:
        _model = Detoxify("original")
    return _model


def _classify_severity(score: float) -> str:
    if score > 0.75:
        return "Vulgar"
    if score > 0.50:
        return "High"
    if score > 0.25:
        return "Medium"
    return "Low"


def analyze_comments(comments: list[dict]) -> pd.DataFrame:
    """
    Analyze comments for toxicity with full sub-label breakdown.

    Returns DataFrame with columns:
    Username, Comment, Toxicity Score, Severity,
    Toxic, Obscene, Threat, Insult, Identity Attack
    """
    model = _get_model()
    rows = []

    for item in comments:
        text = item["comment"]
        res = model.predict(text)

        toxicity_score = round(max(res.values()), 4)
        severity = _classify_severity(toxicity_score)

        rows.append({
            "Username":        item["username"],
            "Comment":         text,
            "Toxicity Score":  toxicity_score,
            "Severity":        severity,
            "Toxic":           round(res.get("toxicity", 0), 3),
            "Obscene":         round(res.get("obscene", 0), 3),
            "Threat":          round(res.get("threat", 0), 3),
            "Insult":          round(res.get("insult", 0), 3),
            "Identity Attack": round(res.get("identity_attack", 0), 3),
        })

    return pd.DataFrame(rows)
