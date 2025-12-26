from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


class SchemaError(ValueError):
    pass


def _pick_first_existing(columns: Iterable[str], candidates: Iterable[str]) -> str:
    col_set = {c for c in columns}
    for c in candidates:
        if c in col_set:
            return c
    raise SchemaError(
        "Não encontrei as colunas esperadas. "
        f"Disponíveis: {sorted(col_set)}. "
        f"Esperadas (qualquer uma): {list(candidates)}"
    )


def load_votes_csv(csv_path: str | Path) -> pd.DataFrame:
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)

    ts_col = _pick_first_existing(
        df.columns,
        [
            "timestamp",
            "Carimbo de data/hora",
            "Carimbo de data/hora ",
            "Timestamp",
        ],
    )
    email_col = _pick_first_existing(
        df.columns,
        ["email", "Endereço de e-mail", "Endereço de e-mail ", "E-mail", "Email"],
    )
    choice_col = _pick_first_existing(
        df.columns,
        [
            "Noel escolhido",
            "Qual o seu Noel favorito?",
            "Qual o seu Noel favorito? ",
            "choice",
        ],
    )

    out = df.copy()
    out["timestamp"] = pd.to_datetime(out[ts_col], dayfirst=True, errors="coerce")
    out["email"] = out[email_col].astype(str).str.strip().str.lower()
    out["choice"] = out[choice_col].astype(str).str.strip()

    keep_cols: list[str] = ["timestamp", "email", "choice"]
    for c in df.columns:
        if c in {ts_col, email_col, choice_col}:
            continue
        if c in keep_cols:
            continue
        keep_cols.append(c)
    out = out[keep_cols]
    out = out.dropna(subset=["timestamp"]).reset_index(drop=True)
    return out


def load_context_markdown(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")
