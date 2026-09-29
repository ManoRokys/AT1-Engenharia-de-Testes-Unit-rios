# PRD - Especificação de Requisitos

## 1. Visão Geral
O sistema avalia solicitações de empréstimo pessoal considerando idade, renda, dívidas atuais, score de crédito e tipo de cliente (VIP ou padrão). O objetivo é determinar a elegibilidade, aprovar ou reprovar a proposta e calcular as parcelas mensais.

## 2. Requisitos Funcionais (RF)
- **RF01:** Validar idade (18 a 75 anos).
- **RF02:** Validar renda (maior que 0) e dívidas existentes (não negativas).
- **RF03:** Reprovar se a dívida atual exceder 70% da renda mensal.
- **RF04:** Classificar o cliente em Tiers pelo score:
  - **Bronze** (300 a 499): limite de 2x a renda, taxa de 15,0% a.a.
  - **Silver** (500 a 699): limite de 5x a renda, taxa de 10,0% a.a.
  - **Gold** (700 a 899): limite de 10x a renda, taxa de 6,5% a.a.
  - **Platinum** (900 a 1000): limite de 15x a renda, taxa de 3,5% a.a.
- **RF05:** Validar prazo (6 a 72 meses) e valor solicitado (mínimo R$ 1.000,00 e até o limite do tier).
- **RF06:** Aplicar 1,0% de desconto na taxa para cliente VIP em prazos de até 24 meses (piso de 2,0% a.a.).
- **RF07:** Calcular parcela mensal (Tabela Price) e reprovar se o comprometimento total com dívidas + nova parcela superar 30% da renda.

## 3. Matriz de Limites (BVA e EP)

### Idade (18 a 75 anos)
| Entrada | Tipo | Resultado Esperado |
|---|---|---|
| 17 | BVA | `IdadeInvalidaError` |
| 18 | BVA | Válido |
| 75 | BVA | Válido |
| 76 | BVA | `IdadeInvalidaError` |

### Score (0 a 1000)
| Entrada | Tipo | Resultado |
|---|---|---|
| -1 | BVA | `ScoreInvalidoError` |
| 0 a 299 | BVA/EP | `ScoreMuitoBaixoError` |
| 300 a 499 | EP | Categoria BRONZE |
| 500 a 699 | EP | Categoria SILVER |
| 700 a 899 | EP | Categoria GOLD |
| 900 a 1000 | EP | Categoria PLATINUM |
| 1001 | BVA | `ScoreInvalidoError` |

### Prazo (6 a 72 meses)
| Entrada | Tipo | Resultado |
|---|---|---|
| 5 | BVA | `PrazoInvalidoError` |
| 6 | BVA | Válido |
| 72 | BVA | Válido |
| 73 | BVA | `PrazoInvalidoError` |
