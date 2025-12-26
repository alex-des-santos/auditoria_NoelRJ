from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .cleaning import apply_user_rules
from .config import AuditConfig
from .suspicion import (
    SuspicionSummary,
    detect_hourly_outliers,
    flag_suspicious_votes,
    hourly_counts,
    summarize_suspicion,
)


@dataclass(frozen=True)
class AuditArtifacts:
    raw: pd.DataFrame
    cleaned: pd.DataFrame
    flagged_raw: pd.DataFrame
    hourly: pd.DataFrame
    hourly_outliers: pd.DataFrame
    suspicion_summary: SuspicionSummary


def build_audit_artifacts(raw_votes: pd.DataFrame, cfg: AuditConfig) -> AuditArtifacts:
    cleaned, raw_enriched = apply_user_rules(raw_votes, cfg)

    flagged_raw = flag_suspicious_votes(raw_enriched, cfg)
    suspicion_summary = summarize_suspicion(flagged_raw)

    hourly = hourly_counts(raw_enriched)
    hourly_outliers = detect_hourly_outliers(hourly)

    return AuditArtifacts(
        raw=raw_votes,
        cleaned=cleaned,
        flagged_raw=flagged_raw,
        hourly=hourly,
        hourly_outliers=hourly_outliers,
        suspicion_summary=suspicion_summary,
    )

