import math
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
    ResultadoAnalise,
    StatusAnalise,
)


class CreditEngine:
    """Motor de análise de crédito e cálculo de parcelas de empréstimo."""

    IDADE_MINIMA = 18
    IDADE_MAXIMA = 75
    SCORE_MINIMO_VALIDO = 0
    SCORE_MAXIMO_VALIDO = 1000
    SCORE_MINIMO_ELEGIVEL = 300
    VALOR_EMPRESTIMO_MINIMO = 1000.0
    PRAZO_MINIMO_MESES = 6
    PRAZO_MAXIMO_MESES = 72
    MARGEM_RISCO_DIVIDA_MAXIMA = 0.70
    MARGEM_CONSIGNAVEL_MAXIMA = 0.30
    PISO_TAXA_JUROS_ANUAL = 2.0

    def analisar_proposta(self, proposta: PropostaEmprestimo) -> ResultadoAnalise:
        cliente = proposta.cliente

        self._validar_cliente(cliente)

        razao_divida = cliente.divida_mensal / cliente.renda_mensal
        if razao_divida > self.MARGEM_RISCO_DIVIDA_MAXIMA:
            return ResultadoAnalise(
                status=StatusAnalise.REPROVADO_ALTO_RISCO,
                mensagem="Proposta reprovada: comprometimento de dívida pré-existente excede 70% da renda mensal.",
                comprometimento_renda_pct=round(razao_divida * 100, 2),
            )

        categoria, multiplicador_renda, taxa_juros_anual = self._determinar_categoria_e_taxa(
            score=cliente.score_credito,
            e_vip=cliente.e_vip,
            prazo_meses=proposta.prazo_meses,
        )

        limite_maximo = cliente.renda_mensal * multiplicador_renda
        self._validar_proposta(proposta, limite_maximo)

        valor_parcela, custo_total, total_juros = self._calcular_financiamento(
            valor=proposta.valor_solicitado,
            taxa_anual=taxa_juros_anual,
            prazo_meses=proposta.prazo_meses,
        )

        divida_total_mensal = cliente.divida_mensal + valor_parcela
        comprometimento_pct = (divida_total_mensal / cliente.renda_mensal) * 100

        if (divida_total_mensal / cliente.renda_mensal) > self.MARGEM_CONSIGNAVEL_MAXIMA:
            return ResultadoAnalise(
                status=StatusAnalise.REPROVADO_MARGEM_INSUFICIENTE,
                mensagem="Proposta reprovada: parcela mensal mais dívidas excedem a margem máxima de 30% da renda.",
                categoria=categoria,
                taxa_juros_anual=taxa_juros_anual,
                valor_solicitado=proposta.valor_solicitado,
                prazo_meses=proposta.prazo_meses,
                valor_parcela_mensal=round(valor_parcela, 2),
                custo_total_emprestimo=round(custo_total, 2),
                total_juros=round(total_juros, 2),
                comprometimento_renda_pct=round(comprometimento_pct, 2),
            )

        return ResultadoAnalise(
            status=StatusAnalise.APROVADO,
            mensagem="Proposta de empréstimo aprovada com sucesso.",
            categoria=categoria,
            taxa_juros_anual=taxa_juros_anual,
            valor_solicitado=proposta.valor_solicitado,
            prazo_meses=proposta.prazo_meses,
            valor_parcela_mensal=round(valor_parcela, 2),
            custo_total_emprestimo=round(custo_total, 2),
            total_juros=round(total_juros, 2),
            comprometimento_renda_pct=round(comprometimento_pct, 2),
        )

    def _validar_cliente(self, cliente: ClienteProfile) -> None:
        if (
            isinstance(cliente.idade, bool)
            or not isinstance(cliente.idade, int)
            or cliente.idade < self.IDADE_MINIMA
            or cliente.idade > self.IDADE_MAXIMA
        ):
            raise IdadeInvalidaError(
                f"Idade inválida: {cliente.idade}. Deve ser um número inteiro entre {self.IDADE_MINIMA} e {self.IDADE_MAXIMA} anos."
            )

        if (
            isinstance(cliente.renda_mensal, bool)
            or not isinstance(cliente.renda_mensal, (int, float))
            or math.isnan(cliente.renda_mensal)
            or math.isinf(cliente.renda_mensal)
            or cliente.renda_mensal <= 0
        ):
            raise RendaInvalidaError(
                f"Renda mensal inválida: {cliente.renda_mensal}. Deve ser um valor numérico estritamente positivo."
            )

        if (
            isinstance(cliente.divida_mensal, bool)
            or not isinstance(cliente.divida_mensal, (int, float))
            or math.isnan(cliente.divida_mensal)
            or math.isinf(cliente.divida_mensal)
            or cliente.divida_mensal < 0
        ):
            raise DividaInvalidaError(
                f"Dívida mensal inválida: {cliente.divida_mensal}. Não pode ser negativa ou não-numérica."
            )

        if (
            isinstance(cliente.score_credito, bool)
            or not isinstance(cliente.score_credito, int)
            or cliente.score_credito < self.SCORE_MINIMO_VALIDO
            or cliente.score_credito > self.SCORE_MAXIMO_VALIDO
        ):
            raise ScoreInvalidoError(
                f"Score de crédito inválido: {cliente.score_credito}. Deve estar entre {self.SCORE_MINIMO_VALIDO} e {self.SCORE_MAXIMO_VALIDO}."
            )

        if cliente.score_credito < self.SCORE_MINIMO_ELEGIVEL:
            raise ScoreMuitoBaixoError(
                f"Score insuficiente para crédito: {cliente.score_credito}. Mínimo necessário é {self.SCORE_MINIMO_ELEGIVEL}."
            )

    def _determinar_categoria_e_taxa(
        self, score: int, e_vip: bool, prazo_meses: int
    ) -> tuple[CategoriaCliente, float, float]:
        if score <= 499:
            categoria = CategoriaCliente.BRONZE
            multiplicador = 2.0
            taxa_base = 15.0
        elif score <= 699:
            categoria = CategoriaCliente.SILVER
            multiplicador = 5.0
            taxa_base = 10.0
        elif score <= 899:
            categoria = CategoriaCliente.GOLD
            multiplicador = 10.0
            taxa_base = 6.5
        else:
            categoria = CategoriaCliente.PLATINUM
            multiplicador = 15.0
            taxa_base = 3.5

        taxa_final = taxa_base
        if e_vip and prazo_meses <= 24:
            taxa_final = max(taxa_base - 1.0, self.PISO_TAXA_JUROS_ANUAL)

        return categoria, multiplicador, taxa_final

    def _validar_proposta(self, proposta: PropostaEmprestimo, limite_maximo: float) -> None:
        if (
            isinstance(proposta.prazo_meses, bool)
            or not isinstance(proposta.prazo_meses, int)
            or proposta.prazo_meses < self.PRAZO_MINIMO_MESES
            or proposta.prazo_meses > self.PRAZO_MAXIMO_MESES
        ):
            raise PrazoInvalidoError(
                f"Prazo inválido: {proposta.prazo_meses}. Deve ser um inteiro entre {self.PRAZO_MINIMO_MESES} e {self.PRAZO_MAXIMO_MESES} meses."
            )

        if (
            isinstance(proposta.valor_solicitado, bool)
            or not isinstance(proposta.valor_solicitado, (int, float))
            or math.isnan(proposta.valor_solicitado)
            or math.isinf(proposta.valor_solicitado)
            or proposta.valor_solicitado < self.VALOR_EMPRESTIMO_MINIMO
            or proposta.valor_solicitado > limite_maximo
        ):
            raise ValorEmprestimoInvalidoError(
                f"Valor solicitado inválido: R$ {proposta.valor_solicitado}. Deve estar entre R$ {self.VALOR_EMPRESTIMO_MINIMO:.2f} e R$ {limite_maximo:.2f} para o perfil do cliente."
            )

    def _calcular_financiamento(
        self, valor: float, taxa_anual: float, prazo_meses: int
    ) -> tuple[float, float, float]:
        taxa_decimal_anual = taxa_anual / 100.0
        taxa_mensal = (1.0 + taxa_decimal_anual) ** (1.0 / 12.0) - 1.0

        fator = (1.0 + taxa_mensal) ** prazo_meses
        parcela_mensal = valor * (taxa_mensal * fator) / (fator - 1.0)
        custo_total = parcela_mensal * prazo_meses
        total_juros = custo_total - valor

        return parcela_mensal, custo_total, total_juros
