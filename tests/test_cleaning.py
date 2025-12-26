from __future__ import annotations

import pandas as pd

from oscar_noel_audit.config import AuditConfig
from oscar_noel_audit.cleaning import apply_user_rules


def test_apply_user_rules_excludes_days_and_dedupes() -> None:
    cfg = AuditConfig.default()
    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2025-12-19 10:00:00",
                    "2025-12-19 10:01:00",
                    "2025-12-20 10:00:00",
                    "2025-12-23 10:00:00",
                ]
            ),
            "email": [
                "a@x.com",
                "a@x.com",
                "b@x.com",
                "c@x.com",
            ],
            "choice": ["X", "X", "Y", "Z"],
        }
    )

    cleaned, enriched = apply_user_rules(df, cfg)

    assert int(enriched["exclude_day"].sum()) == 1
    assert cleaned["email"].tolist() == ["a@x.com", "c@x.com"]
    assert cleaned["choice"].tolist() == ["X", "Z"]


def test_apply_user_rules_filters_plus_pattern() -> None:
    cfg = AuditConfig.default()
    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2025-12-19 10:00:00", "2025-12-19 10:00:10"]
            ),
            "email": ["nome.sobrenome+123@gmail.com", "ok@x.com"],
            "choice": ["X", "Y"],
        }
    )

    cleaned, _ = apply_user_rules(df, cfg)
    assert cleaned["email"].tolist() == ["ok@x.com"]

