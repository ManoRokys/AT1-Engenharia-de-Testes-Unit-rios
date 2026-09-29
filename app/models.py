from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CategoriaCliente(str, Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


class StatusAnalise(str, Enum):
    APROVADO = "APROVADO"
    REPROVADO_ALTO_RISCO = "REPROVADO_ALTO_RISCO"
    REPROVADO_MARGEM_INSUFICIENTE = "REPROVADO_MARGEM_INSUFICIENTE"


@dataclass(frozen=True)
class ClienteProfile:
    idade: int
    renda_mensal: float
    divida_mensal: float
    score_credito: int
    e_vip: bool = False


@dataclass(frozen=True)
class PropostaEmprestimo:
    cliente: ClienteProfile
    valor_solicitado: float
    prazo_meses: int


@dataclass(frozen=True)
class ResultadoAnalise:
    status: StatusAnalise
    mensagem: str
    categoria: Optional[CategoriaCliente] = None
    taxa_juros_anual: Optional[float] = None
    valor_solicitado: float = 0.0
    prazo_meses: int = 0
    valor_parcela_mensal: float = 0.0
    custo_total_emprestimo: float = 0.0
    total_juros: float = 0.0
    comprometimento_renda_pct: float = 0.0
