# Contribuição

## Ambiente

Use Python 3.13 e instale o projeto com as dependências de desenvolvimento:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,build]"
```

Para CMD, ative com `.venv\Scripts\activate.bat`.

## Verificações locais

Antes de enviar mudanças, execute:

```powershell
python -m pytest
python -m ruff check src tests scripts whisper_transcriber.py
python -m ruff format --check src tests scripts whisper_transcriber.py
```

O pipeline do GitHub Actions roda os mesmos testes e lint em Windows com Python 3.13.

## Convenções

- Mantenha código da aplicação em `src/tradutor_ao_vivo/`.
- Mantenha testes em `tests/`, com foco em lógica determinística e sem capturar áudio real.
- Mantenha operações auxiliares em `scripts/` e empacotamento em `packaging/`.
- Adicione dependências de runtime a `[project].dependencies` em `pyproject.toml`; ferramentas de desenvolvimento vão em `[project.optional-dependencies].dev`.
- Não adicione áudio, credenciais, documentos de sessão nem modelos baixados ao controle de versão.
- Preserve o processamento local e a regra de não abrir o microfone.
- Preserve a identidade VoxNexo: navy, blue, cyan e superfícies claras; use a Manrope empacotada para não depender de fontes instaladas.
- Atualize `README.md` e `ARCHITECTURE.md` quando mudar os fluxos de uso ou as fronteiras dos componentes.

## Build do instalador

No Windows, instale o Inno Setup 6 e execute `scripts\build_windows.bat`. Os artefatos são gerados sob `dist/` e não devem ser versionados.
