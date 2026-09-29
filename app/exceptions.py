class CreditEngineError(Exception):
    """Exceção base do motor de crédito."""
    pass


class IdadeInvalidaError(CreditEngineError):
    pass


class ScoreInvalidoError(CreditEngineError):
    pass


class ScoreMuitoBaixoError(CreditEngineError):
    pass


class RendaInvalidaError(CreditEngineError):
    pass


class DividaInvalidaError(CreditEngineError):
    pass


class ValorEmprestimoInvalidoError(CreditEngineError):
    pass


class PrazoInvalidoError(CreditEngineError):
    pass
