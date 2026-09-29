import pytest
from app.credit_engine import CreditEngine
from app.models import ClienteProfile, PropostaEmprestimo


@pytest.fixture
def engine() -> CreditEngine:
    return CreditEngine()


@pytest.fixture
def perfil_padrao_gold() -> ClienteProfile:
    return ClienteProfile(
        idade=35,
        renda_mensal=10000.0,
        divida_mensal=1000.0,
        score_credito=750,
        e_vip=False,
    )


@pytest.fixture
def proposta_valida_gold(perfil_padrao_gold: ClienteProfile) -> PropostaEmprestimo:
    return PropostaEmprestimo(
        cliente=perfil_padrao_gold,
        valor_solicitado=20000.0,
        prazo_meses=24,
    )
