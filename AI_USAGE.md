# Relatório de Uso de IA (AI_USAGE.md)

## Ferramenta Utilizada
- **Assistente de IA:** Antigravity AI (Gemini 3.6 Flash)
- **Modo:** Pair programming / apoio no desenvolvimento dos testes e estrutura do repositório.

## Como a IA foi utilizada
- Auxílio na criação da estrutura de arquivos do projeto com `uv`.
- Geração de rascunho dos cenários de teste limite (BVA/EP) com `@pytest.mark.parametrize`.
- Apoio na identificação dos casos de *error guessing* (tipos incorretos, `NaN`, `Inf`).

## Processo de Auditoria Humana
- **Revisão de Código:** Validação manual de todas as regras de negócio em `app/credit_engine.py` para garantir tratamento defensivo de tipos (ex: `isinstance(x, bool)`).
- **Validação de Testes:** Verificação linha a linha das asserções e conferência de execução no terminal via `uv run pytest --cov=app --cov-branch`.
- **Autonomia:** Todo o código, testes e definições de regras foram revisados e testados antes da entrega final.
