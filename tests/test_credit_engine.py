from typing import Any
import pytest

from app.credit_engine import CreditEngine
from app.exceptions import (
    DividaInvalidaError,
    IdadeInvalidaError,
    PrazoInvalidoError,
    RendaInvalidaError,
    ScoreInvalidoError,
    ScoreMuitoBaixoError,
    ValorEmprestimoInvalidoError,
)
from app.models import (
    CategoriaCliente,
    ClienteProfile,
    PropostaEmprestimo,
    StatusAnalise,
)


@pytest.mark.unit
class TestCreditEngineSucesso:

    def test_aprovacao_proposta_gold_sucesso(
        self, engine: CreditEngine, proposta_valida_gold: PropostaEmprestimo
    ) -> None:
        # Arrange
        proposta = proposta_valida_gold

        # Act
        resultado = engine.analisar_proposta(proposta)

        # Assert
        assert resultado.status == StatusAnalise.APROVADO
        assert resultado.categoria == CategoriaCliente.GOLD
        assert resultado.taxa_juros_anual == 6.5
        assert resultado.valor_solicitado == 20000.0
        assert resultado.prazo_meses == 24
        assert resultado.valor_parcela_mensal > 0.0
        assert resultado.custo_total_emprestimo > 20000.0
        assert resultado.total_juros > 0.0
        assert resultado.comprometimento_renda_pct <= 30.0
        assert "aprovada com sucesso" in resultado.mensagem

    def test_desconto_vip_prazo_curto_sucesso(self, engine: CreditEngine) -> None:
        # Arrange
        cliente_vip = ClienteProfile(
            idade=40,
            renda_mensal=15000.0,
            divida_mensal=0.0,
            score_credito=950,
            e_vip=True,
        )
        proposta = PropostaEmprestimo(
            cliente=cliente_vip, valor_solicitado=50000.0, prazo_meses=24
        )

        # Act
        resultado = engine.analisar_proposta(proposta)

        # Assert
        assert resultado.status == StatusAnalise.APROVADO
        assert resultado.categoria == CategoriaCliente.PLATINUM
        assert resultado.taxa_juros_anual == 2.5

    def test_vip_prazo_longo_sem_desconto(self, engine: CreditEngine) -> None:
        # Arrange
        cliente_vip = ClienteProfile(
            idade=40,
            renda_mensal=15000.0,
            divida_mensal=0.0,
            score_credito=950,
            e_vip=True,
        )
        proposta = PropostaEmprestimo(
            cliente=cliente_vip, valor_solicitado=50000.0, prazo_meses=36
        )

        # Act
        resultado = engine.analisar_proposta(proposta)

        # Assert
        assert resultado.status == StatusAnalise.APROVADO
        assert resultado.taxa_juros_anual == 3.5

    def test_piso_taxa_juros_regulatorio_vip(self, engine: CreditEngine) -> None:
        # Arrange
        _, _, taxa = engine._determinar_categoria_e_taxa(
            score=950, e_vip=True, prazo_meses=12
        )
        # Act
        taxa_piso = max(2.5 - 1.0, engine.PISO_TAXA_JUROS_ANUAL)

        # Assert
        assert taxa == 2.5
        assert taxa_piso == 2.0


@pytest.mark.unit
class TestCreditEngineParticionamentoEquivalencia:

    @pytest.mark.parametrize(
        "score, categoria_esperada, taxa_esperada, max_multiplicador",
        [
            (350, CategoriaCliente.BRONZE, 15.0, 2.0),
            (600, CategoriaCliente.SILVER, 10.0, 5.0),
            (800, CategoriaCliente.GOLD, 6.5, 10.0),
            (950, CategoriaCliente.PLATINUM, 3.5, 15.0),
        ],
    )
    def test_ep_classificacao_categorias_score(
        self,
        engine: CreditEngine,
        score: int,
        categoria_esperada: CategoriaCliente,
        taxa_esperada: float,
        max_multiplicador: float,
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=30,
            renda_mensal=5000.0,
            divida_mensal=0.0,
            score_credito=score,
            e_vip=False,
        )
        proposta = PropostaEmprestimo(
            cliente=cliente, valor_solicitado=1000.0, prazo_meses=12
        )

        # Act
        resultado = engine.analisar_proposta(proposta)

        # Assert
        assert resultado.status == StatusAnalise.APROVADO
        assert resultado.categoria == categoria_esperada
        assert resultado.taxa_juros_anual == taxa_esperada


@pytest.mark.unit
class TestCreditEngineAnaliseValorLimite:

    @pytest.mark.parametrize(
        "idade, e_valido",
        [
            (17, False),
            (18, True),
            (19, True),
            (74, True),
            (75, True),
            (76, False),
        ],
    )
    def test_bva_idade_cliente(
        self, engine: CreditEngine, idade: int, e_valido: bool
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=idade,
            renda_mensal=10000.0,
            divida_mensal=0.0,
            score_credito=700,
        )
        proposta = PropostaEmprestimo(cliente=cliente, valor_solicitado=5000.0, prazo_meses=12)

        # Act & Assert
        if e_valido:
            resultado = engine.analisar_proposta(proposta)
            assert resultado.status == StatusAnalise.APROVADO
        else:
            with pytest.raises(IdadeInvalidaError):
                engine.analisar_proposta(proposta)

    @pytest.mark.parametrize(
        "score, excecao_esperada",
        [
            (-1, ScoreInvalidoError),
            (0, ScoreMuitoBaixoError),
            (299, ScoreMuitoBaixoError),
            (300, None),
            (499, None),
            (500, None),
            (699, None),
            (700, None),
            (899, None),
            (900, None),
            (1000, None),
            (1001, ScoreInvalidoError),
        ],
    )
    def test_bva_score_credito(
        self, engine: CreditEngine, score: int, excecao_esperada: type | None
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=30,
            renda_mensal=10000.0,
            divida_mensal=0.0,
            score_credito=score,
        )
        proposta = PropostaEmprestimo(cliente=cliente, valor_solicitado=1000.0, prazo_meses=12)

        # Act & Assert
        if excecao_esperada:
            with pytest.raises(excecao_esperada):
                engine.analisar_proposta(proposta)
        else:
            resultado = engine.analisar_proposta(proposta)
            assert resultado.status == StatusAnalise.APROVADO

    @pytest.mark.parametrize(
        "prazo, e_valido",
        [
            (5, False),
            (6, True),
            (7, True),
            (71, True),
            (72, True),
            (73, False),
        ],
    )
    def test_bva_prazo_meses(
        self, engine: CreditEngine, prazo: int, e_valido: bool
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=30, renda_mensal=10000.0, divida_mensal=0.0, score_credito=700
        )
        proposta = PropostaEmprestimo(cliente=cliente, valor_solicitado=5000.0, prazo_meses=prazo)

        # Act & Assert
        if e_valido:
            resultado = engine.analisar_proposta(proposta)
            assert resultado.status == StatusAnalise.APROVADO
        else:
            with pytest.raises(PrazoInvalidoError):
                engine.analisar_proposta(proposta)

    def test_bva_valor_solicitado_limite_minimo_e_maximo(
        self, engine: CreditEngine
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=30, renda_mensal=5000.0, divida_mensal=0.0, score_credito=750
        )

        # Act & Assert: Abaixo do mínimo R$ 1.000,00
        proposta_abaixo_min = PropostaEmprestimo(
            cliente=cliente, valor_solicitado=999.99, prazo_meses=12
        )
        with pytest.raises(ValorEmprestimoInvalidoError):
            engine.analisar_proposta(proposta_abaixo_min)

        # Act & Assert: Mínimo R$ 1.000,00
        proposta_minima = PropostaEmprestimo(
            cliente=cliente, valor_solicitado=1000.0, prazo_meses=12
        )
        res_min = engine.analisar_proposta(proposta_minima)
        assert res_min.status == StatusAnalise.APROVADO

        # Act & Assert: Limite máximo R$ 50.000,00
        proposta_maxima = PropostaEmprestimo(
            cliente=cliente, valor_solicitado=50000.0, prazo_meses=72
        )
        res_max = engine.analisar_proposta(proposta_maxima)
        assert res_max.status in (
            StatusAnalise.APROVADO,
            StatusAnalise.REPROVADO_MARGEM_INSUFICIENTE,
        )

        # Act & Assert: Acima do máximo R$ 50.000,01
        proposta_acima_max = PropostaEmprestimo(
            cliente=cliente, valor_solicitado=50000.01, prazo_meses=12
        )
        with pytest.raises(ValorEmprestimoInvalidoError):
            engine.analisar_proposta(proposta_acima_max)


@pytest.mark.unit
class TestCreditEngineRegrasRiscoEMargem:

    def test_reprovacao_alto_risco_divida_existente_acima_70_porcento(
        self, engine: CreditEngine
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=30, renda_mensal=10000.0, divida_mensal=7001.0, score_credito=800
        )
        proposta = PropostaEmprestimo(
            cliente=cliente, valor_solicitado=5000.0, prazo_meses=12
        )

        # Act
        resultado = engine.analisar_proposta(proposta)

        # Assert
        assert resultado.status == StatusAnalise.REPROVADO_ALTO_RISCO
        assert "excede 70% da renda" in resultado.mensagem
        assert resultado.comprometimento_renda_pct == 70.01

    def test_aprovacao_divida_existente_exatamente_70_porcento(
        self, engine: CreditEngine
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=30, renda_mensal=100000.0, divida_mensal=70000.0, score_credito=800
        )
        proposta = PropostaEmprestimo(
            cliente=cliente, valor_solicitado=1000.0, prazo_meses=72
        )

        # Act
        resultado = engine.analisar_proposta(proposta)

        # Assert
        assert resultado.status == StatusAnalise.REPROVADO_MARGEM_INSUFICIENTE

    def test_reprovacao_margem_insuficiente_dti_excede_30_porcento(
        self, engine: CreditEngine
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=30, renda_mensal=4000.0, divida_mensal=1000.0, score_credito=700
        )
        proposta = PropostaEmprestimo(
            cliente=cliente, valor_solicitado=10000.0, prazo_meses=12
        )

        # Act
        resultado = engine.analisar_proposta(proposta)

        # Assert
        assert resultado.status == StatusAnalise.REPROVADO_MARGEM_INSUFICIENTE
        assert "excedem a margem máxima de 30%" in resultado.mensagem
        assert resultado.comprometimento_renda_pct > 30.0


@pytest.mark.unit
class TestCreditEngineErrorGuessing:

    @pytest.mark.parametrize(
        "valor_idade, excecao",
        [
            ("30", IdadeInvalidaError),
            (30.5, IdadeInvalidaError),
            (True, IdadeInvalidaError),
            (None, IdadeInvalidaError),
            (0, IdadeInvalidaError),
            (-25, IdadeInvalidaError),
        ],
    )
    def test_error_guessing_idade_invalida(
        self, engine: CreditEngine, valor_idade: Any, excecao: type
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=valor_idade, renda_mensal=5000.0, divida_mensal=0.0, score_credito=700
        )
        proposta = PropostaEmprestimo(cliente=cliente, valor_solicitado=2000.0, prazo_meses=12)

        # Act & Assert
        with pytest.raises(excecao):
            engine.analisar_proposta(proposta)

    @pytest.mark.parametrize(
        "valor_renda, excecao",
        [
            (0, RendaInvalidaError),
            (-5000.0, RendaInvalidaError),
            ("5000", RendaInvalidaError),
            (True, RendaInvalidaError),
            (float("nan"), RendaInvalidaError),
            (float("inf"), RendaInvalidaError),
        ],
    )
    def test_error_guessing_renda_invalida(
        self, engine: CreditEngine, valor_renda: Any, excecao: type
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=30, renda_mensal=valor_renda, divida_mensal=0.0, score_credito=700
        )
        proposta = PropostaEmprestimo(cliente=cliente, valor_solicitado=1000.0, prazo_meses=12)

        # Act & Assert
        with pytest.raises(excecao):
            engine.analisar_proposta(proposta)

    @pytest.mark.parametrize(
        "valor_divida, excecao",
        [
            (-1.0, DividaInvalidaError),
            ("100", DividaInvalidaError),
            (True, DividaInvalidaError),
            (float("nan"), DividaInvalidaError),
            (float("inf"), DividaInvalidaError),
        ],
    )
    def test_error_guessing_divida_invalida(
        self, engine: CreditEngine, valor_divida: Any, excecao: type
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=30, renda_mensal=5000.0, divida_mensal=valor_divida, score_credito=700
        )
        proposta = PropostaEmprestimo(cliente=cliente, valor_solicitado=1000.0, prazo_meses=12)

        # Act & Assert
        with pytest.raises(excecao):
            engine.analisar_proposta(proposta)

    @pytest.mark.parametrize(
        "valor_prazo, excecao",
        [
            (12.5, PrazoInvalidoError),
            ("12", PrazoInvalidoError),
            (True, PrazoInvalidoError),
            (0, PrazoInvalidoError),
        ],
    )
    def test_error_guessing_prazo_invalido(
        self, engine: CreditEngine, valor_prazo: Any, excecao: type
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=30, renda_mensal=5000.0, divida_mensal=0.0, score_credito=700
        )
        proposta = PropostaEmprestimo(cliente=cliente, valor_solicitado=1000.0, prazo_meses=valor_prazo)

        # Act & Assert
        with pytest.raises(excecao):
            engine.analisar_proposta(proposta)

    @pytest.mark.parametrize(
        "valor_solicitado, excecao",
        [
            ("1000", ValorEmprestimoInvalidoError),
            (True, ValorEmprestimoInvalidoError),
            (float("nan"), ValorEmprestimoInvalidoError),
            (float("inf"), ValorEmprestimoInvalidoError),
        ],
    )
    def test_error_guessing_valor_solicitado_invalido(
        self, engine: CreditEngine, valor_solicitado: Any, excecao: type
    ) -> None:
        # Arrange
        cliente = ClienteProfile(
            idade=30, renda_mensal=5000.0, divida_mensal=0.0, score_credito=700
        )
        proposta = PropostaEmprestimo(cliente=cliente, valor_solicitado=valor_solicitado, prazo_meses=12)

        # Act & Assert
        with pytest.raises(excecao):
            engine.analisar_proposta(proposta)
