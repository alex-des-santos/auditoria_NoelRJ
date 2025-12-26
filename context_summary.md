# Contexto da Auditoria - Oscar Noel RJ 2025

## Resumo Executivo

Esta auditoria foi realizada sobre uma votação online para escolher o "Melhor Papai Noel do Rio de Janeiro 2025". A análise dos **14.790 votos** coletados entre 11/12/2025 e 26/12/2025 revelou **sinais massivos de manipulação automatizada** que comprometem a integridade do resultado.

## Dados Analisados

### Campos Disponíveis
O dataset contém apenas 3 campos:
- **Timestamp**: Data e hora do voto
- **Email**: Endereço de email do votante
- **Candidato**: Nome do Papai Noel escolhido

### Período da Votação
- **Início**: 11/12/2025
- **Término**: 26/12/2025
- **Total de respostas**: 14.790 votos

### Limitações dos Dados
⚠️ **Importante**: O CSV não contém:
- Endereço IP dos votantes
- User-Agent (navegador/dispositivo)
- Identificador de dispositivo
- Dados de geolocalização

Isso limita algumas análises (como clustering por IP), mas os padrões de email e timing são suficientes para detectar manipulação.

## Principais Descobertas

### 1. Padrão Massivo de Emails Sintéticos

Foi identificado um padrão extremamente suspeito de emails seguindo o formato:
```
nome.sobrenome###@gmail.com
```

Onde `###` representa exatamente 3 dígitos (ex: `maria.silva123@gmail.com`, `joao.santos456@gmail.com`)

**Estatísticas do Padrão:**
- **8.577 emails** seguem este padrão (58% do total bruto)
- **99,75%** desses votos foram para um único candidato
- Apareceram concentrados em apenas 5 dias (18-22/12)
- Pool pequeno de nomes repetidos centenas de vezes

Este é um sinal clássico de geração automatizada de identidades por scripts.

### 2. Explosão de Volume em Janela Curta

| Data | Votos Totais | Votos com Padrão Suspeito | % do Dia |
|------|--------------|---------------------------|----------|
| 18/12 | 901 | 367 | 40,7% |
| 19/12 | 1.926 | 1.235 | 64,1% |
| **20/12** | **2.486** | **1.758** | **70,7%** |
| **21/12** | **3.668** | **3.094** | **84,4%** |
| **22/12** | **2.623** | **2.118** | **80,8%** |

O pico de **3.668 votos em 21/12** representa **24,8% de todo o dataset**, com **84,4% seguindo o padrão suspeito**.

### 3. Concentração Extrema em Um Candidato

Quando analisamos os votos com padrão `nome.sobrenome###@gmail.com`:

- **MÁRIO ROQUE - SHOPPING METROPOLITANO BARRA**: 99,75% dos votos
- Outros 11 candidatos: 0,25% dos votos (residual)

Esta concentração é **estatisticamente impossível** em votação orgânica e indica campanha automatizada focada.

### 4. Repetição Patológica de Emails

Foram detectados casos extremos de repetição:
- **1 email votou 1.102 vezes** (todos para SAYMON CLAUS)
- **1.446 votos duplicados** mesmo após remover dias 20-22
- Timing entre votos duplicados é humanamente impossível (< 1 segundo)

### 5. Outros Sinais de Automação

**Domínios Inválidos:**
- Emails com typos: `gmail.cm`, `gmail.con`, `gmail.comj`
- Indicam geração automática sem validação

**Intervalos Anormais:**
- Votos consecutivos com < 0,5 segundos de diferença
- Impossível de realizar manualmente

**Horários Incomuns:**
- Picos de votação na madrugada (0h-5h)
- Padrão incompatível com comportamento humano orgânico

## Impacto no Resultado

### Cenário A: Regras Básicas (Dias 20-22 + Deduplicação)
**4.567 votos válidos**

| Posição | Candidato | Votos | % |
|---------|-----------|-------|---|
| 1º | MÁRIO ROQUE - SHOPPING METROPOLITANO BARRA | 1.858 | 40,68% |
| 2º | MARCUS SOUZA - PÁTIO ALCANTRA | 946 | 20,71% |
| 3º | CÉSAR FERNANDO - SIDER SHOPPING | 821 | 17,98% |

### Cenário B: Remove Padrão Suspeito (nome.sobrenome###)
**2.982 votos válidos**

| Posição | Candidato | Votos | % |
|---------|-----------|-------|---|
| 1º | **MARCUS SOUZA - PÁTIO ALCANTRA** | 944 | 31,66% |
| 2º | **CÉSAR FERNANDO - SIDER SHOPPING** | 820 | 27,50% |
| 3º | **MÁRIO ROQUE - SHOPPING METROPOLITANO BARRA** | 277 | 9,29% |

### ⚠️ Mudança Crítica

O vencedor **muda completamente** entre os cenários:
- **Cenário A**: MÁRIO ROQUE com 40,68%
- **Cenário B**: MÁRIO ROQUE cai para **3º lugar com 9,29%**

Esta inversão dramática confirma que o padrão suspeito teve **impacto massivo e determinante** no resultado.

## Metodologia de Detecção

### Regras Aplicadas

1. **Exclusão de Dias Específicos**
   - Dias 20, 21 e 22/12 foram removidos por concentrarem volume anormal

2. **Deduplicação de Emails**
   - Mantida apenas a primeira ocorrência de cada email
   - Remove spam repetido do mesmo endereço

3. **Detecção de Padrões Sintéticos**
   - Regex: `^[a-z]+\.[a-z]+\d{3}@gmail\.com$`
   - Identifica emails gerados automaticamente

4. **Análise de Intervalos**
   - Delta mínimo entre votos consecutivos
   - Delta mínimo entre votos no mesmo candidato

5. **Detecção de Horários Incomuns**
   - Votos na madrugada (0h-5h) são marcados

6. **Validação de Domínios**
   - Detecção de typos comuns (gmail.cm, gmail.con)

## Conclusões

### Sobre Este Resultado

1. ✅ **Cenário B é mais confiável** - Remove manipulação automatizada clara
2. ✅ **Documentar critérios de exclusão** - Transparência é essencial
3. ✅ **Manter evidências** - Este relatório serve como documentação

### Para Votações Futuras

**Recomendações Técnicas:**

1. **Verificação de Email**
   - Implementar confirmação por email (double opt-in)
   - Validar domínios existentes

2. **CAPTCHA**
   - Adicionar reCAPTCHA v3 ou similar
   - Dificulta automação em massa

3. **Rate Limiting**
   - Limitar votos por IP/dispositivo
   - Bloquear requisições muito rápidas

4. **Normalização de Emails**
   - Gmail ignora pontos: `john.doe@gmail.com` = `johndoe@gmail.com`
   - Remover aliases com `+`: `user+tag@gmail.com` → `user@gmail.com`
   - Previne variações do mesmo email

5. **Monitoramento em Tempo Real**
   - Alertas de picos anormais
   - Dashboard de métricas ao vivo
   - Detecção precoce de ataques

6. **Bloqueio de Padrões**
   - Rejeitar emails com padrões suspeitos
   - Lista de domínios permitidos (whitelist)

## Referências Técnicas

### Conceitos Aplicados

- **Gmail Dot Blindness**: Gmail ignora pontos no endereço local
- **Plus Addressing**: Aliases com `+` permitem múltiplas variações
- **OWASP Automated Threats**: "Skewing" - distorção de métricas por automação
- **MAD Z-Score**: Detecção de outliers robusta a extremos

### Fontes

- Google Support - Como funcionam os endereços do Gmail
- OWASP - Automated Threat Handbook
- Guias de detecção de bot traffic (Cloudflare, Akamai)

## Notas Importantes

⚠️ **Privacidade**: Todos os dados apresentados nesta aplicação:
- Emails são convertidos em hashes SHA-256 (não reversíveis)
- Nenhum dado pessoal é exposto publicamente
- CSV limpo exportado não contém informações identificáveis

✅ **Integridade**: Esta análise é:
- Reproduzível (código open source)
- Baseada em critérios objetivos e documentados
- Transparente em suas limitações
