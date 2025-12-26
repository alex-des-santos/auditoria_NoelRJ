from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import AuditConfig


@dataclass(frozen=True)
class SuspicionSummary:
    global_short_deltas: int
    per_choice_short_deltas: int
    night_votes: int
    suspicious_domains: int
    synthetic_email_suffix3: int
    max_votes_same_email: int


def flag_suspicious_votes(raw_enriched: pd.DataFrame, cfg: AuditConfig) -> pd.DataFrame:
    df = raw_enriched.sort_values("timestamp", kind="mergesort").copy()

    df["delta_prev_seconds"] = df["timestamp"].diff().dt.total_seconds()
    df["flag_global_short_delta"] = df["delta_prev_seconds"].fillna(np.inf) <= cfg.min_global_delta_seconds

    df["choice_delta_prev_seconds"] = (
        df.groupby("choice")["timestamp"].diff().dt.total_seconds()
    )
    df["flag_choice_short_delta"] = (
        df["choice_delta_prev_seconds"].fillna(np.inf) <= cfg.min_per_choice_delta_seconds
    )

    start_h, end_h = cfg.night_hours
    df["flag_night_vote"] = df["hour"].between(start_h, end_h, inclusive="both")

    df["flag_suspicious_domain_typo"] = df["email"].str.contains(
        cfg.suspicious_domains_regex, regex=True, na=False
    )

    df["flag_synthetic_email_suffix3"] = df["email"].apply(
        lambda e: bool(cfg.suspicious_email_suffix3_regex.match(e))
    )

    return df


def summarize_suspicion(flags_df: pd.DataFrame) -> SuspicionSummary:
    email_counts = flags_df["email"].value_counts(dropna=False)
    max_votes_same_email = int(email_counts.max()) if not email_counts.empty else 0

    return SuspicionSummary(
        global_short_deltas=int(flags_df["flag_global_short_delta"].sum()),
        per_choice_short_deltas=int(flags_df["flag_choice_short_delta"].sum()),
        night_votes=int(flags_df["flag_night_vote"].sum()),
        suspicious_domains=int(flags_df["flag_suspicious_domain_typo"].sum()),
        synthetic_email_suffix3=int(flags_df["flag_synthetic_email_suffix3"].sum()),
        max_votes_same_email=max_votes_same_email,
    )


def hourly_counts(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["hour_bucket"] = out["timestamp"].dt.floor("h")
    g = out.groupby("hour_bucket").size().rename("votes").reset_index()
    return g


def detect_hourly_outliers(hourly: pd.DataFrame, z_thresh: float = 3.5) -> pd.DataFrame:
    if hourly.empty:
        return hourly.assign(z=np.nan, is_outlier=False)

    votes = hourly["votes"].astype(float)
    med = float(votes.median())
    mad = float((votes - med).abs().median())
    if mad == 0.0:
        z = (votes - med).abs()
    else:
        z = 0.6745 * (votes - med) / mad

    out = hourly.copy()
    out["z"] = z
    out["is_outlier"] = out["z"].abs() >= z_thresh
    return out

