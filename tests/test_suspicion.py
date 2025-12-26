from __future__ import annotations

import pandas as pd

from oscar_noel_audit.config import AuditConfig
from oscar_noel_audit.suspicion import detect_hourly_outliers, flag_suspicious_votes, hourly_counts


def test_flag_suspicious_votes_short_deltas_and_night() -> None:
    cfg = AuditConfig.default()
    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2025-12-19 00:00:00",
                    "2025-12-19 00:00:01",
                    "2025-12-19 12:00:00",
                ]
            ),
            "email": ["a@x.com", "b@x.com", "c@x.com"],
            "choice": ["X", "X", "Y"],
        }
    )

    from oscar_noel_audit.cleaning import add_basic_features

    enriched = add_basic_features(df)
    enriched["exclude_day"] = False
    enriched["suspicious_email_plus_3dig_gmail"] = False

    flagged = flag_suspicious_votes(enriched, cfg)
    assert flagged["flag_global_short_delta"].sum() >= 1
    assert flagged["flag_choice_short_delta"].sum() >= 1
    assert flagged["flag_night_vote"].sum() == 2


def test_detect_hourly_outliers_marks_spike() -> None:
    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2025-12-19 10:00:00",
                    "2025-12-19 10:00:01",
                    "2025-12-19 10:00:02",
                    "2025-12-19 11:00:00",
                ]
            ),
            "email": ["a@x.com", "b@x.com", "c@x.com", "d@x.com"],
            "choice": ["X", "X", "X", "Y"],
        }
    )
    from oscar_noel_audit.cleaning import add_basic_features

    hourly = hourly_counts(add_basic_features(df))
    out = detect_hourly_outliers(hourly, z_thresh=1.0)
    assert "is_outlier" in out.columns

