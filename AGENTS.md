# AGENTS.md - Governança de Agentes de IA e Instruções do Repositório

Este arquivo estabelece as diretrizes de instrução e governança para agentes de Inteligência Artificial (incluindo Cursor, Antigravity, Claude, GitHub Copilot ou similares) que atuem neste repositório.

## 1. Princípios de Governança e Autonomia
- **Transparência:** Todas as gerações de código e artefatos de teste devem ser auditadas por humanos.
- **Não Regressão de Cobertura:** Nenhuma alteração pode reduzir a cobertura de ramificação (`--cov-branch`) abaixo de **100%**.
- **Determinismo:** O código de negócio não pode utilizar estados globais, geradores aleatórios sem seed ou chamadas de I/O externas não mockadas.

## 2. Comandos do Gerenciador de Projeto (`uv`)
Para executar os testes e validar a cobertura no projeto, os agentes devem sugerir/utilizar os comandos oficiais via `uv`:

```bash
# Instalar dependências no ambiente virtual .venv
uv sync

# Executar a suíte de testes unitários em modo detalhado
uv run pytest -v

# Executar a verificação rigorosa de cobertura de código e ramificações (100% de branch coverage)
uv run pytest --cov=app --cov-branch --cov-report=term-missing
```

## 3. Diretrizes de Engenharia de Testes (QTS)
1. **Padrão AAA Mandatório:** Todo teste unitário deve explicitar os blocos `# Arrange`, `# Act` e `# Assert`.
2. **Defesa contra Falsos Positivos:** Não utilizar `try...except` genérico nos testes para capturar exceções; utilizar obrigatoriamente `with pytest.raises(ExcecaoEsperada):`.
3. **Validação de Limites (BVA):** Exigido para idade (17, 18, 19, 74, 75, 76), score (-1, 0, 299, 300, 499, 500, 699, 700, 899, 900, 1000, 1001), prazos (5, 6, 72, 73) e valores de empréstimo (999.99, 1000.00, limite max, limite max + 0.01).
