async function loadAnalysis() {
  const res = await fetch("data/analysis.json");
  if (!res.ok) throw new Error("Falha ao carregar data/analysis.json");
  return await res.json();
}

function fmtInt(n) {
  return new Intl.NumberFormat("pt-BR").format(n);
}
function fmtPct(x) {
  return (x * 100).toFixed(2).replace(".", ",") + "%";
}

function setKpis(analysis) {
  const A = analysis.scenarios.A_regras_do_usuario.total;
  const B = analysis.scenarios.B_remove_padrao_nome_sobrenome_3dig_gmail.total;
  const C = analysis.scenarios.C_conservador.total;

  document.getElementById("kpiTotalA").textContent = fmtInt(A);
  document.getElementById("kpiTotalB").textContent = fmtInt(B);
  document.getElementById("kpiTotalC").textContent = fmtInt(C);
}

function renderRanking(analysis, scenarioKey) {
  const s = analysis.scenarios[scenarioKey];
  const tbody = document.querySelector("#rankingTable tbody");
  tbody.innerHTML = "";

  for (const row of s.top) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.name}</td>
      <td>${fmtInt(row.votes)}</td>
      <td>${fmtPct(row.share)}</td>
    `;
    tbody.appendChild(tr);
  }

  const labels = s.top.slice(0, 8).map(d => d.name);
  const values = s.top.slice(0, 8).map(d => d.votes);
  const total = s.total;

  Plotly.newPlot("pieScenario", [{
    type: "pie",
    labels,
    values,
    textinfo: "label+percent",
    hovertemplate: "%{label}<br>%{value} votos<br>%{percent}<extra></extra>",
    sort: false
  }], {
    margin: {t: 10, r: 10, b: 10, l: 10},
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    showlegend: false
  }, {displayModeBar: false, responsive: true});

  // Title line (small)
  document.querySelector("#resultados .panel h2");
}

function renderDailyVolume(analysis) {
  const d = analysis.daily;
  const dates = d.map(x => x.date);
  const submissions = d.map(x => x.submissions);
  const unique = d.map(x => x.unique_emails);
  const dup = d.map(x => x.duplicates);

  Plotly.newPlot("chartDailyVolume", [
    { type: "bar", x: dates, y: submissions, name: "Submissões" },
    { type: "scatter", mode: "lines+markers", x: dates, y: unique, name: "E-mails únicos", yaxis: "y2" },
    { type: "scatter", mode: "lines", x: dates, y: dup, name: "Duplicatas", yaxis: "y2" }
  ], {
    margin: {t: 10, r: 40, b: 50, l: 50},
    barmode: "overlay",
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    xaxis: { tickangle: -35, showgrid: false },
    yaxis: { title: "Submissões", gridcolor: "rgba(255,255,255,0.06)" },
    yaxis2: { title: "Únicos/Duplicatas", overlaying: "y", side: "right", gridcolor: "rgba(255,255,255,0)" },
    legend: { orientation: "h", x: 0, y: -0.25 }
  }, {displayModeBar: false, responsive: true});
}

function renderDailyShares(analysis) {
  const d = analysis.daily;
  const dates = d.map(x => x.date);
  const mario = d.map(x => x.mario_share);
  const pattern = d.map(x => x.pattern_share);

  Plotly.newPlot("chartDailyShares", [
    { type: "scatter", mode: "lines+markers", x: dates, y: mario, name: "Share do MÁRIO ROQUE" },
    { type: "scatter", mode: "lines+markers", x: dates, y: pattern, name: "Share do padrão suspeito" }
  ], {
    margin: {t: 10, r: 20, b: 50, l: 50},
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    xaxis: { tickangle: -35, showgrid: false },
    yaxis: { tickformat: ".0%", gridcolor: "rgba(255,255,255,0.06)" },
    legend: { orientation: "h", x: 0, y: -0.25 }
  }, {displayModeBar: false, responsive: true});
}

async function main() {
  const analysis = await loadAnalysis();

  setKpis(analysis);
  renderDailyVolume(analysis);
  renderDailyShares(analysis);

  const sel = document.getElementById("scenario");
  const render = () => renderRanking(analysis, sel.value);
  sel.addEventListener("change", render);
  render();
}

main().catch(err => {
  console.error(err);
  alert("Erro ao carregar a página de análise. Veja o console.");
});
