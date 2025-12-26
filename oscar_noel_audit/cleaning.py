from __future__ import annotations

import pandas as pd

from .config import AuditConfig


def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["date"] = out["timestamp"].dt.date
    out["day"] = out["timestamp"].dt.day
    out["hour"] = out["timestamp"].dt.hour
    out["email_domain"] = out["email"].str.split("@").str[-1]
    return out


def apply_user_rules(df: pd.DataFrame, cfg: AuditConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    enriched = add_basic_features(df)

    enriched["exclude_day"] = enriched["day"].isin(cfg.excluded_days)
    enriched["suspicious_email_plus_3dig_gmail"] = enriched["email"].apply(
        lambda e: bool(cfg.suspicious_email_plus_regex.match(e))
    )

    pre_filtered = enriched[~enriched["exclude_day"]].copy()
    pre_filtered = pre_filtered.sort_values("timestamp", kind="mergesort")
    cleaned = pre_filtered.drop_duplicates(subset=["email"], keep="first").copy()
    cleaned = cleaned[~cleaned["suspicious_email_plus_3dig_gmail"]].copy()
    cleaned = cleaned.reset_index(drop=True)

    return cleaned, enriched

