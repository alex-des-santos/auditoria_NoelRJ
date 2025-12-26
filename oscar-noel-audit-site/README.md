# Auditoria de Votação — Oscar Noel RJ 2025

Página estática (GitHub Pages) para apresentar uma auditoria/EDA de uma votação online, com foco em sinais de automação e robustez do resultado.

## O que esta página mostra
- **Cenários A/B/C** com ranking e participação
- **Séries diárias**: submissões, e-mails únicos, duplicatas
- **Indicadores**: share diário de um candidato e share diário de um padrão suspeito

## Privacidade (importante)
Este repositório foi estruturado para ser **público sem expor PII** (ex.: emails).
- Coloque o CSV original em `data/private/` (ignorando pelo `.gitignore`)
- Gere somente agregados/relatórios públicos (ex.: `data/analysis.json`)

## Como publicar no GitHub Pages
1. Faça o commit do repositório
2. Settings → Pages → Deploy from branch (ex.: `main` / `/root`)
3. Acesse a URL gerada

## Fontes (para contextualização de abuso automatizado)
- Gmail ignora pontos em endereços (variações com/sem ponto chegam no mesmo inbox): Google Support
- “Plus addressing” (`usuario+tag@gmail.com`) é um recurso usado para aliases: Gmail/Google Support
- OWASP Automated Threats: “skewing” inclui repetição de submissões para distorcer métricas
- Sinais de bot traffic incluem picos inesperados e padrões anormais: guias de bot traffic

> Dica: cite essas fontes na descrição do projeto no GitHub/README para justificar as decisões de auditoria.
