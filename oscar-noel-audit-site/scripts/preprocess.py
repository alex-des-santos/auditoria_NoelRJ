"""Preprocessador (privado) para gerar agregados públicos.

Uso:
  python scripts/preprocess.py data/private/respostas.csv

Saída:
  data/analysis.json

Objetivo:
  - Carregar dados brutos (com emails)
  - Aplicar filtros (dias/duplicatas/padrões)
  - Gerar agregados públicos (sem emails)

Obs.: mantenha o CSV original fora do GitHub (data/private/ no .gitignore).
"""
import sys, re, json
import pandas as pd
from datetime import datetime

EXCLUDED_DAYS = {20, 21, 22}

PATTERN_NAME_DOT_NAME_3DIG_GMAIL = re.compile(r'^[a-z]+(?:\.[a-z]+)+\d{3}@gmail\.com$')

def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["Carimbo de data/hora"], dayfirst=True, errors="coerce")
    df["email"] = df["Endereço de e-mail"].astype(str).str.strip().str.lower()
    df["choice"] = df["Qual o seu Noel favorito?"].astype(str).str.strip()
    df["day"] = df["timestamp"].dt.day
    df["exclude_day"] = df["day"].isin(EXCLUDED_DAYS)
    df["pattern_suspeito"] = df["email"].apply(lambda x: bool(PATTERN_NAME_DOT_NAME_3DIG_GMAIL.match(x)))
    return df

def dedupe_keep_first(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values("timestamp").drop_duplicates("email", keep="first")

def rank(df: pd.DataFrame, top_n: int = 12):
    vc = df["choice"].value_counts()
    total = int(vc.sum())
    top = vc.head(top_n)
    return {"total": total, "top": [{"name": k, "votes": int(v), "share": float(v/total)} for k, v in top.items()]}

def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/preprocess.py <caminho_csv>")
        sys.exit(1)

    raw_path = sys.argv[1]
    raw = load_csv(raw_path)

    # Cenário A: regras do organizador (exclui dias + dedupe email)
    A = dedupe_keep_first(raw[~raw["exclude_day"]].copy())

    # Cenário B: A + remove padrão suspeito
    B = A[~A["pattern_suspeito"]].copy()

    # Cenário C: placeholder conservador (adicione regras extras se quiser)
    C = B.copy()

    daily = raw.assign(date=raw["timestamp"].dt.date).groupby("date").agg(
        submissions=("email", "size"),
        unique_emails=("email", "nunique"),
        duplicates=("email", lambda s: s.size - s.nunique()),
        mario_votes=("choice", lambda s: (s == "MÁRIO ROQUE - SHOPPING METROPOLITANO BARRA").sum()),
        mario_share=("choice", lambda s: (s == "MÁRIO ROQUE - SHOPPING METROPOLITANO BARRA").mean()),
        pattern_votes=("pattern_suspeito", "sum"),
        pattern_share=("pattern_suspeito", "mean"),
    ).reset_index()

    out = {
        "title": "Auditoria de Votação — Oscar Noel RJ 2025",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "rules": {
            "exclude_days": ["2025-12-20", "2025-12-21", "2025-12-22"],
            "dedupe_email_exact": True,
            "bot_patterns": [{"id":"regex_nome_sobrenome_3dig_gmail", "pattern": PATTERN_NAME_DOT_NAME_3DIG_GMAIL.pattern}]
        },
        "scenarios": {
            "A_regras_do_usuario": rank(A),
            "B_remove_padrao_nome_sobrenome_3dig_gmail": rank(B),
            "C_conservador": rank(C)
        },
        "daily": daily.to_dict(orient="records")
    }

    with open("data/analysis.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("OK: data/analysis.json atualizado (sem emails).")

if __name__ == "__main__":
    main()
