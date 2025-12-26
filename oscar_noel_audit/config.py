from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class AuditConfig:
    excluded_days: set[int]
    suspicious_email_plus_regex: re.Pattern[str]
    suspicious_email_suffix3_regex: re.Pattern[str]
    suspicious_domains_regex: re.Pattern[str]
    night_hours: tuple[int, int]
    min_global_delta_seconds: float
    min_per_choice_delta_seconds: float

    @staticmethod
    def default() -> "AuditConfig":
        return AuditConfig(
            excluded_days={20, 21, 22},
            suspicious_email_plus_regex=re.compile(
                r"^[a-z]+(?:\.[a-z]+)+\+\d{3}@gmail\.com$"
            ),
            suspicious_email_suffix3_regex=re.compile(
                r"^[a-z]+(?:\.[a-z]+)+\d{3}@gmail\.com$"
            ),
            suspicious_domains_regex=re.compile(
                r"@(?:gmail\.cm|gmail\.con|gmail\.comj|gmal\.com|gmial\.com)$"
            ),
            night_hours=(0, 5),
            min_global_delta_seconds=2.0,
            min_per_choice_delta_seconds=2.0,
        )

