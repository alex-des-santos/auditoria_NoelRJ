# Análise Técnica Completa - Oscar Noel RJ 2025

## Visão Geral dos Dados

O dataset contém **14.790 votos** coletados entre **11/12/2025** e **26/12/2025**, com apenas 3 campos:
- **timestamp**: Data e hora do voto
- **email**: Endereço de email do votante
- **Noel escolhido**: Nome do candidato

## Cenário A: Aplicação de Regras Básicas

As seguintes regras de validação foram aplicadas:

* Exclusão de votos nos dias **20/12, 21/12, 22/12**
* Deduplicação por email (mantida primeira ocorrência)
* Validação do padrão "`nome.sobrenome+123@gmail.com`" (não detectado no dataset)

### Resultados da Filtragem Básica

* Total bruto: **14.790**
* Removidos por dia (20–22): **8.777**
* Sobraram: **6.013**
* Removidos por duplicidade de email (nesses dias restantes): **1.446**
* **Votos válidos finais (suas regras): 4.567**

### Ranking - Cenário A

| Posição | Candidato | Votos | Percentual |
|---------|-----------|-------|------------|
| 1º | M**** R**** – SHOPPING M***********O B***A | 1.858 | 40,68% |
| 2º | M***** S**** – PÁTIO A******** | 946 | 20,71% |
| 3º | C**** F******* – SIDER SHOPPING | 821 | 17,98% |

> **Nota de qualidade**: Foram identificadas duas variações para um candidato (**"SAYMON CLAUS..."** e **"SAYMON ..."**). Caso sejam o mesmo candidato, o total combinado seria 211 votos, sem impacto no ranking dos 3 primeiros.

## Padrões de Manipulação Detectados

A exclusão dos dias 20-22 remove volume anormal, mas não elimina o padrão de manipulação mais significativo. A análise temporal revela que o comportamento anômalo **inicia em 18/12** e atinge pico entre 19-22/12.

### Padrão Crítico: Emails Sintéticos

Foi identificado um padrão massivo de emails seguindo o formato:

**`nome.sobrenome###@gmail.com`** (exatamente 3 dígitos no final, sem o caractere "+")

#### Características do Padrão

Nos **4.567 votos válidos** após regras básicas:

* **1.585 emails** (34,7%) seguem este padrão
* **99,75%** desses votos concentram-se em **Candidato A** (M**** R****)

Esta concentração extrema é incompatível com votação orgânica e sugere **geração automatizada de identidades** (lista restrita de nomes + sufixo numérico aleatório). Este comportamento é característico de ataques automatizados a formulários online.

#### Distribuição Temporal do Padrão

* 18/12: 367 envios nesse padrão
* 19/12: 1.235
* 20/12: 1.758
* 21/12: 3.094
* 22/12: 2.118

Em todos estes dias, ~100% dos votos com o padrão foram para o **Candidato A**.

### Padrão Secundário: Pool Limitado de Prefixos

Análise dos emails únicos revela concentração em poucos prefixos repetidos dezenas de vezes (ex.: `lucas.pereira###`, `beatriz.souza###`). Este comportamento é consistente com scripts que selecionam prefixos de uma lista limitada e geram sufixos numéricos aleatórios.

### Padrão Terciário: Repetição Extrema por Email

Foram detectadas **1.446 submissões duplicadas** por email, mesmo excluindo os dias 20-22. Distribuição:

* Maioria das duplicatas: **Candidato D** (788 votos)
* Caso extremo: **1 único email com 1.102 votos**, todos para o **Candidato D**

Este volume de repetição é incompatível com interação manual humana, indicando automação (script ou pressionamento automatizado de teclas).

### Padrão Auxiliar: Domínios Inválidos

Foram identificados emails com domínios malformados: `gmail.cm`, `gmail.con`, `gmail.comj`, etc.

Possíveis causas:
* Ausência de validação de domínio no formulário
* Geração automatizada de endereços sem validação de formato

## Comparação de Cenários de Filtragem

Para uma apuração defensável, é necessário tratar o padrão `nome.sobrenome###@gmail.com`:

### Cenário A: Regras Básicas

**4.567 votos válidos**

| Posição | Candidato | Votos | Percentual |
|---------|-----------|-------|------------|
| 1º | Candidato A | 1.858 | 40,68% |
| 2º | Candidato B | 946 | 20,71% |
| 3º | Candidato C | 821 | 17,98% |

### Cenário B: Remove Padrão `nome.sobrenome###@gmail.com`

**2.982 votos válidos**

| Posição | Candidato | Votos | Percentual |
|---------|-----------|-------|------------|
| 1º | Candidato B | 944 | 31,66% |
| 2º | Candidato C | 820 | 27,50% |
| 3º | Candidato A | 277 | 9,29% |

### Cenário C: Conservador (Remove Padrão + Outros Suspeitos)

**2.855 votos válidos**

| Posição | Candidato | Votos | Percentual |
|---------|-----------|-------|------------|
| 1º | Candidato B | 889 | 31,14% |
| 2º | Candidato C | 792 | 27,74% |
| 3º | Candidato A | 274 | 9,60% |

## Critérios de Detecção de Comportamento Automatizado

Por ordem de prioridade:

1. **Pico de volume temporal** + **concentração extrema** (>99%) em um candidato
2. **Identidades sintéticas em massa** (template repetido milhares de vezes)
3. **Repetição patológica por email** (centenas/milhares de submissões do mesmo endereço)
4. **Domínios inválidos/typos** (sinal auxiliar de validação ausente)

### Nota Técnica: Gmail Dot Blindness

O Gmail ignora pontos no prefixo do endereço ("dot blindness"), ou seja, `nome.sobrenome@gmail.com` e `nomesobrenome@gmail.com` são o mesmo endereço. Este é um vetor clássico para burlar deduplicação.

**Análise**: Não foram detectadas variantes exploitando este vetor no dataset analisado. Recomenda-se normalização de emails Gmail em votações futuras para prevenir este ataque.

## Impacto nos Resultados

A aplicação do **Cenário B** (recomendado) resulta em:

* **Mudança completa do vencedor**: Candidato A cai de 1º (40,68%) para 3º (9,29%)
* **Inversão do ranking**: Candidato B assume 1º lugar com 31,66%

Esta inversão dramática demonstra o **impacto massivo e determinante** do padrão de emails sintéticos no resultado da votação.

## Recomendações

### Para Esta Votação
* Utilizar **Cenário B ou C** como resultado oficial
* Documentar critérios de exclusão aplicados
* Manter transparência sobre metodologia

### Para Votações Futuras
* Implementar verificação de email (confirmação dupla)
* Adicionar CAPTCHA
* Aplicar rate limiting por IP/dispositivo
* Normalizar emails Gmail (remover pontos, aliases com +)
* Bloquear padrões conhecidos de emails sintéticos
* Validar domínios de email
* Monitorar picos em tempo real
