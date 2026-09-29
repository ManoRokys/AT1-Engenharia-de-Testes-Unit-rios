# Motor de Análise de Crédito - QTS AT1

Trabalho prático de Engenharia de Testes Unitários, Cobertura de Código e Governança de IA para a disciplina de Qualidade e Teste de Software (FATEC).

## Estrutura do Projeto

- `app/`: Código fonte da aplicação (SUT) e exceções.
- `tests/`: Suíte de testes unitários com Pytest.
- `PRD.md`: Especificação dos requisitos e regras de negócio.
- `AGENTS.md` e `.cursorrules`: Regras de governança de código e testes.
- `AI_USAGE.md`: Relatório de transparência sobre o uso de IA.
- `ROTEIRO_VIDEO.md`: Roteiro simplificado para a gravação da apresentação em vídeo.

## Como Executar

### 1. Instalar dependências com `uv`
```bash
uv sync
```

### 2. Executar os testes unitários
```bash
uv run pytest -v
```

### 3. Verificar a cobertura de código (100% de cobertura de ramificação)
```bash
uv run pytest --cov=app --cov-branch --cov-report=term-missing
```

## Cobertura de Testes

```text
Name                   Stmts   Miss Branch BrPart    Cover   Missing
--------------------------------------------------------------------
app\__init__.py            4      0      0      0  100.00%
app\credit_engine.py      74      0     26      0  100.00%
app\exceptions.py         16      0      0      0  100.00%
app\models.py             27      0      0      0  100.00%
--------------------------------------------------------------------
TOTAL                    121      0     26      0  100.00%
```

## Link do Vídeo

- **Link da apresentação:** (https://youtu.be/Vy7fU5RNNLM)
