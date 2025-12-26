from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from oscar_noel_audit import AuditConfig, build_audit_artifacts, load_context_markdown, load_votes_csv


def _default_paths() -> tuple[Path, Path]:
    root = Path(__file__).resolve().parent
    csv_path = root / "Oscar Noel 2025 (respostas) - Respostas ao formulário 1.csv"
    ctx_path = root / "context.md"
    return csv_path, ctx_path


def _hash_email(email: str) -> str:
    return sha256(email.encode("utf-8")).hexdigest()[:12]


def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        key = cand.lower()
        if key in cols:
            return cols[key]
    return None


@st.cache_data(show_spinner=False)
def _load_raw(csv_path: str) -> pd.DataFrame:
    return load_votes_csv(csv_path)


@st.cache_data(show_spinner=False)
def _load_context(path: str) -> str:
    return load_context_markdown(path)


def _censor_name(name: str) -> str:
    """
    Censura nomes de candidatos para anonimização.
    Mantém primeira letra de cada palavra e substitui demais por asteriscos.
    """
    import re

    # Split by common separators (space, dash)
    parts = re.split(r'(\s*-\s*|\s+)', name)
    censored_parts = []

    for part in parts:
        # Keep separators as-is
        if re.match(r'^\s*-\s*$|^\s+$', part):
            censored_parts.append(part)
            continue

        # Split into words
        words = part.split()
        censored_words = []

        for word in words:
            if len(word) <= 2:
                # Keep very short words
                censored_words.append(word)
            else:
                # First letter + asterisks for rest
                censored = word[0] + '*' * (len(word) - 1)
                censored_words.append(censored)

        censored_parts.append(' '.join(censored_words))

    return ''.join(censored_parts)


def main() -> None:
    st.set_page_config(page_title="Auditoria — Oscar Noel RJ 2025", layout="wide")
    st.title("Auditoria — Oscar Noel RJ 2025")

    default_csv, default_ctx = _default_paths()

    with st.sidebar:
        st.header("Entradas")

        # File upload option
        uploaded_file = st.file_uploader(
            "Faça upload do CSV de votação",
            type=['csv'],
            help="Arquivo CSV com as colunas: timestamp, email, candidato"
        )

        # Use uploaded file or default path
        if uploaded_file is not None:
            import tempfile
            import os
            # Save uploaded file to temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                csv_path = tmp_file.name
        else:
            # Try to use default path if it exists
            if default_csv.exists():
                csv_path = str(default_csv)
            else:
                st.warning("⚠️ Nenhum arquivo CSV foi carregado. Por favor, faça upload de um arquivo para continuar.")
                st.stop()

        ctx_path = st.text_input("Contexto (Markdown)", value=str(default_ctx))

        st.header("Regras de Filtragem")
        excluded_days_str = st.text_input("Dias excluídos (DD, separados por vírgula)", value="20,21,22")

        st.markdown("**Detecção de Intervalos Suspeitos**")
        st.caption("Votos com intervalo muito curto podem indicar automação")
        min_global = st.slider(
            "Intervalo mínimo entre votos consecutivos (segundos)",
            0.0, 10.0, 2.0, 0.5,
            help="Tempo mínimo entre qualquer voto. Votos mais rápidos que isso são marcados como suspeitos."
        )
        min_choice = st.slider(
            "Intervalo mínimo entre votos no mesmo candidato (segundos)",
            0.0, 10.0, 2.0, 0.5,
            help="Tempo mínimo entre votos no mesmo candidato. Útil para detectar bots focados em um candidato específico."
        )

        st.markdown("**Detecção de Horários Incomuns**")
        night_start, night_end = st.slider(
            "Definir horário da madrugada (horas)",
            0, 23, (0, 5), 1,
            help="Votos neste horário são marcados como suspeitos por serem menos comuns."
        )

        st.markdown("**Privacidade**")
        show_email_hashes = st.checkbox(
            "Mostrar hashes de e-mail (não reversível)",
            value=True,
            help="Exibe hash SHA-256 dos emails para análise sem expor dados pessoais."
        )

        st.markdown("**Nível de Filtragem**")
        filtering_scenario = st.radio(
            "Escolha o cenário de filtragem:",
            ["A - Básico", "B - Rigoroso", "C - Conservador"],
            index=0,
            help="""
            • A: Remove apenas dias 20-22 e duplicatas
            • B: Remove também padrão nome.sobrenome### (Recomendado)
            • C: Remove padrão + domínios typo + plus pattern
            """
        )

    excluded_days = {
        int(x.strip())
        for x in excluded_days_str.split(",")
        if x.strip().isdigit()
    }
    cfg = replace(
        AuditConfig.default(),
        excluded_days=excluded_days,
        min_global_delta_seconds=float(min_global),
        min_per_choice_delta_seconds=float(min_choice),
        night_hours=(int(night_start), int(night_end)),
    )

    raw = _load_raw(csv_path)

    # Apply name censorship to the raw data
    raw["choice"] = raw["choice"].apply(_censor_name)

    artifacts = build_audit_artifacts(raw, cfg)

    # Apply rules based on selected scenario
    if filtering_scenario == "B - Rigoroso":
        # Scenario B: Remove synthetic email pattern
        cleaned = artifacts.flagged_raw[
            (~artifacts.flagged_raw["exclude_day"]) &
            (~artifacts.flagged_raw["flag_synthetic_email_suffix3"])
        ].drop_duplicates("email")
    elif filtering_scenario == "C - Conservador":
        # Scenario C: Remove pattern + other minor suspicious signals
        cleaned = artifacts.flagged_raw[
            (~artifacts.flagged_raw["exclude_day"]) &
            (~artifacts.flagged_raw["flag_synthetic_email_suffix3"]) &
            (~artifacts.flagged_raw["flag_suspicious_domain_typo"]) &
            (~artifacts.flagged_raw["suspicious_email_plus_3dig_gmail"])
        ].drop_duplicates("email")
    else:
        # Scenario A: Basic rules (default)
        cleaned = artifacts.cleaned

    tabs = st.tabs(
        ["Visão geral", "Insights Críticos", "Suspeitas", "Visualizações", "Qualidade", "Contexto"]
    )

    flagged = artifacts.flagged_raw

    with tabs[0]:
        st.subheader("Dados limpos (após regras aplicadas)")

        if filtering_scenario == "A - Básico":
            st.warning("📊 **Cenário A Ativo**: Regras básicas (remove apenas dias 20-22 e duplicatas)")
        elif filtering_scenario == "B - Rigoroso":
            st.info("📊 **Cenário B Ativo**: Regras rigorosas (remove padrão nome.sobrenome###) - **Recomendado**")
        else:
            st.success("📊 **Cenário C Ativo**: Regras conservadoras (remove padrão + domínios typo + plus pattern)")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total bruto", f"{len(raw):,}".replace(",", "."))
        k2.metric("Após excluir dias", f"{len(flagged[~flagged['exclude_day']]):,}".replace(",", "."))
        k3.metric("Após dedupe e-mail", f"{len(flagged[~flagged['exclude_day']].drop_duplicates('email')):,}".replace(",", "."))
        k4.metric("Votos finais", f"{len(cleaned):,}".replace(",", "."))

        top = cleaned["choice"].value_counts().reset_index()
        top.columns = ["choice", "votes"]
        top["share"] = top["votes"] / top["votes"].sum() if len(top) else 0.0

        # Format share as percentage
        top_display = top.head(12).copy()
        top_display["share"] = top_display["share"].apply(lambda x: f"{x*100:.2f}%")

        c1, c2 = st.columns([1.2, 1.0])
        with c1:
            st.markdown("**Ranking (top 12)**")
            st.dataframe(top_display, width="stretch")
        with c2:
            fig = px.pie(
                top.head(8),
                names="choice",
                values="votes",
                title="Participação (top 8)",
            )
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, width="stretch")

    with tabs[1]:
        st.subheader("Insights Críticos da Auditoria")

        st.markdown("""
        ### Principais Achados

        Esta votação apresenta **sinais fortes de manipulação automatizada**. A análise identificou padrões que são
        característicos de ataques de bots a formulários online.
        """)

        st.warning("""
        **Alerta Principal:** Foi detectado um padrão massivo de emails sintéticos do tipo `nome.sobrenome###@gmail.com`
        (onde ### representa exatamente 3 dígitos) que concentrou votos de forma extrema em um único candidato.
        """)

        col1, col2, col3 = st.columns(3)

        # Calculate pattern statistics
        pattern_count = int(flagged["flag_synthetic_email_suffix3"].sum())
        pattern_pct = (pattern_count / len(cleaned) * 100) if len(cleaned) > 0 else 0

        # Get concentration for the top candidate in pattern votes
        pattern_votes = flagged[flagged["flag_synthetic_email_suffix3"] == True]
        if len(pattern_votes) > 0:
            pattern_concentration = (pattern_votes["choice"].value_counts().iloc[0] / len(pattern_votes) * 100) if len(pattern_votes) > 0 else 0
            top_pattern_candidate = pattern_votes["choice"].value_counts().index[0] if len(pattern_votes) > 0 else "N/A"
        else:
            pattern_concentration = 0
            top_pattern_candidate = "N/A"

        col1.metric(
            "Votos com padrão suspeito",
            f"{pattern_count:,}".replace(",", "."),
            f"{pattern_pct:.1f}% do total limpo",
            delta_color="inverse"
        )
        col2.metric(
            "Concentração no padrão",
            f"{pattern_concentration:.1f}%",
            "em um único candidato",
            delta_color="inverse"
        )
        col3.metric(
            "Candidato mais beneficiado",
            top_pattern_candidate if len(top_pattern_candidate) < 20 else top_pattern_candidate[:17] + "...",
            "pelo padrão suspeito",
            delta_color="inverse"
        )

        st.markdown("---")

        st.markdown("""
        ### Por que isso é suspeito?

        1. **Identidades Sintéticas em Massa**
           - O padrão `nome.sobrenome###@gmail.com` apareceu milhares de vezes
           - Pool pequeno de nomes reciclados com diferentes sufixos numéricos
           - Característico de scripts que geram emails automaticamente

        2. **Explosão de Volume em Janela Curta**
           - Pico abrupto de votos nos dias 18-22 de dezembro
           - Volume anormal comparado aos dias anteriores
           - Correlação direta com o aparecimento do padrão suspeito

        3. **Concentração Extrema em Um Candidato**
           - ~99.75% dos votos com esse padrão vão para o mesmo candidato
           - Comportamento incompatível com votação orgânica
           - Sinal clássico de campanha automatizada
        """)

        st.markdown("---")

        st.markdown("### Comparação de Cenários")

        st.markdown("""
        Veja como o resultado muda drasticamente ao aplicar diferentes níveis de filtragem:
        """)

        # Create scenario comparison
        scenario_data = []

        # Scenario A: User rules only (current "cleaned")
        top_a = cleaned["choice"].value_counts().head(3)
        scenario_data.append({
            "Cenário": "A - Regras Básicas",
            "Descrição": "Remove apenas dias 20-22 e duplicatas",
            "Total Votos": len(cleaned),
            "1º Lugar": top_a.index[0] if len(top_a) > 0 else "N/A",
            "Votos 1º": int(top_a.iloc[0]) if len(top_a) > 0 else 0,
            "% 1º": f"{(top_a.iloc[0] / len(cleaned) * 100):.1f}%" if len(cleaned) > 0 and len(top_a) > 0 else "0%"
        })

        # Scenario B: Remove pattern (simulate)
        cleaned_no_pattern = flagged[
            (~flagged["exclude_day"]) &
            (~flagged["flag_synthetic_email_suffix3"])
        ].drop_duplicates("email")

        if len(cleaned_no_pattern) > 0:
            top_b = cleaned_no_pattern["choice"].value_counts().head(3)
            scenario_data.append({
                "Cenário": "B - Remove Padrão Suspeito",
                "Descrição": "Remove padrão nome.sobrenome###",
                "Total Votos": len(cleaned_no_pattern),
                "1º Lugar": top_b.index[0] if len(top_b) > 0 else "N/A",
                "Votos 1º": int(top_b.iloc[0]) if len(top_b) > 0 else 0,
                "% 1º": f"{(top_b.iloc[0] / len(cleaned_no_pattern) * 100):.1f}%" if len(top_b) > 0 else "0%"
            })

        scenario_df = pd.DataFrame(scenario_data)
        st.dataframe(scenario_df, width="stretch", hide_index=True)

        st.info("""
        **Observação:** O vencedor muda completamente entre os cenários A e B, demonstrando o impacto
        massivo do padrão suspeito no resultado da votação.
        """)

        st.markdown("---")

        st.markdown("""
        ### Outros Sinais de Manipulação Detectados

        - **Repetição Patológica:** Um único email enviou mais de 1.100 votos (impossível manualmente)
        - **Domínios Inválidos:** Emails com typos como `gmail.cm`, `gmail.con`, `gmail.comj`
        - **Intervalos Anormais:** Votos consecutivos com tempo humanamente impossível
        - **Padrão de Madrugada:** Concentração incomum de votos em horários atípicos
        """)

        st.markdown("""
        ### Recomendações

        1. **Para Este Resultado:**
           - Considere o Cenário B como mais confiável
           - Documente claramente os critérios de exclusão
           - Mantenha transparência sobre as regras aplicadas

        2. **Para Votações Futuras:**
           - Implemente verificação de email (CAPTCHA, confirmação por email)
           - Adicione rate limiting por IP/dispositivo
           - Bloqueie padrões conhecidos de emails sintéticos
           - Normalize emails do Gmail (remover pontos, aliases com +)
           - Monitore em tempo real para detectar anomalias rapidamente
        """)

    with tabs[2]:
        st.subheader("Sinais de comportamento suspeito (base bruta enriquecida)")
        s = artifacts.suspicion_summary
        a1, a2, a3, a4, a5, a6 = st.columns(6)
        a1.metric("Delta global curto", str(s.global_short_deltas))
        a2.metric("Delta por candidato curto", str(s.per_choice_short_deltas))
        a3.metric("Votos na madrugada", str(s.night_votes))
        a4.metric("Domínio typo", str(s.suspicious_domains))
        a5.metric("Padrão nome.sobrenome###", str(s.synthetic_email_suffix3))
        a6.metric("Máx. votos no mesmo e-mail", str(s.max_votes_same_email))

        ip_col = _find_col(flagged, ["ip", "ip_address", "endereco ip", "endereço ip"])
        ua_col = _find_col(flagged, ["user_agent", "useragent", "navegador", "user agent"])
        device_col = _find_col(flagged, ["device", "dispositivo", "device_id", "device id"])

        if not any([ip_col, ua_col, device_col]):
            st.markdown(
                "Limitação: a base fornecida não contém IP, user-agent ou identificador de dispositivo; "
                "qualquer análise desses itens só é possível se esses campos existirem no CSV."
            )

        sub = flagged.copy()
        if show_email_hashes:
            sub["email_hash"] = sub["email"].map(_hash_email)
            cols = [
                "timestamp",
                "email_hash",
                "choice",
                "flag_global_short_delta",
                "flag_choice_short_delta",
                "flag_night_vote",
                "flag_synthetic_email_suffix3",
                "flag_suspicious_domain_typo",
            ]
        else:
            cols = [
                "timestamp",
                "choice",
                "flag_global_short_delta",
                "flag_choice_short_delta",
                "flag_night_vote",
                "flag_synthetic_email_suffix3",
                "flag_suspicious_domain_typo",
            ]

        suspicious_rows = sub[
            sub["flag_global_short_delta"]
            | sub["flag_choice_short_delta"]
            | sub["flag_night_vote"]
            | sub["flag_synthetic_email_suffix3"]
            | sub["flag_suspicious_domain_typo"]
        ].copy()
        suspicious_rows = suspicious_rows.sort_values("timestamp", ascending=False)
        st.markdown("**Exemplos de votos sinalizados (até 500)**")
        st.dataframe(suspicious_rows[cols].head(500), width="stretch")

        st.markdown("**Repetição por e-mail (base bruta)**")
        repeats = (
            flagged["email"]
            .value_counts()
            .reset_index()
        )
        repeats.columns = ["email", "votes"]
        repeats["votes"] = repeats["votes"].astype(int)
        repeats = repeats[repeats["votes"] > 1].head(50)
        if show_email_hashes and not repeats.empty:
            repeats["email_hash"] = repeats["email"].map(_hash_email)
            repeats = repeats.drop(columns=["email"])
        st.dataframe(repeats, width="stretch")

        cluster_cols = [c for c in [ip_col, ua_col, device_col] if c]
        if cluster_cols:
            st.markdown("**Clusters por origem (top 50)**")
            clusters = (
                flagged.groupby(cluster_cols)
                .size()
                .rename("votes")
                .reset_index()
                .sort_values("votes", ascending=False)
                .head(50)
            )
            st.dataframe(clusters, width="stretch")

    with tabs[3]:
        st.subheader("Visualizações interativas")

        daily = (
            flagged.assign(date=flagged["timestamp"].dt.date)
            .groupby("date")
            .agg(
                submissions=("email", "size"),
                unique_emails=("email", "nunique"),
                duplicates=("email", lambda s: s.size - s.nunique()),
                night_votes=("flag_night_vote", "sum"),
                synthetic_suffix3=("flag_synthetic_email_suffix3", "sum"),
            )
            .reset_index()
        )

        fig_daily = px.line(
            daily,
            x="date",
            y=["submissions", "unique_emails", "duplicates"],
            title="Volume diário (submissões, únicos e duplicatas)",
        )
        fig_daily.update_layout(legend_title_text="", margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_daily, width="stretch")

        heat = (
            flagged.assign(date=flagged["timestamp"].dt.date, hour=flagged["timestamp"].dt.hour)
            .groupby(["date", "hour"])
            .size()
            .rename("votes")
            .reset_index()
        )
        heat_pivot = heat.pivot(index="hour", columns="date", values="votes").fillna(0)
        fig_heat = px.imshow(
            heat_pivot,
            aspect="auto",
            title="Mapa de calor (hora x dia)",
            labels=dict(x="Dia", y="Hora", color="Votos"),
        )
        fig_heat.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_heat, width="stretch")

        outliers = artifacts.hourly_outliers
        fig_hour = px.bar(
            outliers,
            x="hour_bucket",
            y="votes",
            color="is_outlier",
            title="Votos por hora (outliers por MAD-zscore)",
        )
        fig_hour.update_layout(legend_title_text="", margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_hour, width="stretch")

        st.markdown("**Mapa geográfico**")
        lat_col = _find_col(flagged, ["lat", "latitude"])
        lon_col = _find_col(flagged, ["lon", "lng", "longitude", "long"])
        city_col = _find_col(flagged, ["cidade", "city"])
        uf_col = _find_col(flagged, ["uf", "estado", "state"])

        if lat_col and lon_col:
            geo = flagged[[lat_col, lon_col]].copy()
            geo[lat_col] = pd.to_numeric(geo[lat_col], errors="coerce")
            geo[lon_col] = pd.to_numeric(geo[lon_col], errors="coerce")
            geo = geo.dropna(subset=[lat_col, lon_col])
            if geo.empty:
                st.info("Colunas de latitude/longitude existem, mas não há pontos válidos.")
            else:
                fig_map = px.scatter_mapbox(
                    geo,
                    lat=lat_col,
                    lon=lon_col,
                    zoom=8,
                    height=520,
                )
                fig_map.update_layout(mapbox_style="open-street-map", margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_map, width="stretch")
        elif city_col:
            geo_counts = flagged[city_col].astype(str).str.strip().replace({"nan": None}).dropna()
            geo_counts = geo_counts.value_counts().head(30).reset_index()
            geo_counts.columns = ["local", "votes"]
            title = "Top 30 localidades"
            if uf_col:
                title = "Top 30 (cidade/UF) por volume"
                loc = (
                    flagged[[city_col, uf_col]]
                    .astype(str)
                    .apply(lambda r: f"{r[city_col]} / {r[uf_col]}", axis=1)
                )
                geo_counts = loc.value_counts().head(30).reset_index()
                geo_counts.columns = ["local", "votes"]
            st.plotly_chart(px.bar(geo_counts, x="votes", y="local", orientation="h", title=title), width="stretch")
        else:
            st.info(
                "O CSV analisado não traz latitude/longitude ou cidade/UF. "
                "Sem esses campos, não dá para construir um mapa defensável."
            )

    with tabs[4]:
        st.subheader("Métricas de qualidade dos dados")

        excluded = int(flagged["exclude_day"].sum())
        dup_total = int(flagged["email"].size - flagged["email"].nunique())
        plus_pattern = int(flagged["suspicious_email_plus_3dig_gmail"].sum())
        suffix3_pattern = int(flagged["flag_synthetic_email_suffix3"].sum())

        q1, q2, q3, q4 = st.columns(4)
        q1.metric("Removidos por dia 20–22", str(excluded))
        q2.metric("Duplicatas (bruto)", str(dup_total))
        q3.metric("Padrão nome.sobrenome+123", str(plus_pattern))
        q4.metric("Padrão nome.sobrenome123", str(suffix3_pattern))

        st.markdown("**Distribuição por domínio (top 15)**")
        dom = flagged["email_domain"].value_counts().head(15).reset_index()
        dom.columns = ["domain", "votes"]
        st.plotly_chart(
            px.bar(dom, x="domain", y="votes", title="Domínios de e-mail (top 15)"),
            width="stretch",
        )

        st.markdown("**Distribuição por candidato (dados limpos)**")
        st.plotly_chart(
            px.bar(top.head(12), x="votes", y="choice", orientation="h", title="Top 12 (limpo)"),
            width="stretch",
        )

        st.markdown("**Download**")
        anon = cleaned.copy()
        if "email" in anon.columns:
            anon["email_hash"] = anon["email"].map(_hash_email)
            anon = anon.drop(columns=["email"])
        st.download_button(
            "Baixar votos limpos (CSV, sem PII)",
            data=anon.to_csv(index=False).encode("utf-8"),
            file_name="votos_limpos_sem_pii.csv",
            mime="text/csv",
        )

    with tabs[5]:
        st.subheader("Contexto e Metodologia da Auditoria")

        # Toggle between summary and detailed context
        view_mode = st.radio(
            "Selecione o nível de detalhe:",
            ["Resumo Executivo", "Análise Técnica Completa"],
            horizontal=True
        )

        if view_mode == "Resumo Executivo":
            # Load the new descriptive summary
            summary_path = Path(__file__).resolve().parent / "context_summary.md"
            try:
                with open(summary_path, "r", encoding="utf-8") as f:
                    st.markdown(f.read())
            except Exception as e:
                st.error(f"Falha ao carregar resumo: {e}")
                st.info("Certifique-se de que o arquivo 'context_summary.md' existe no diretório raiz do projeto.")
        else:
            # Load the original detailed context
            try:
                st.markdown(_load_context(ctx_path))
            except Exception as e:
                st.error(f"Falha ao carregar context.md: {e}")


if __name__ == "__main__":
    main()
