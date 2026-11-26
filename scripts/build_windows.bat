@echo off
setlocal
for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
pushd "%PROJECT_ROOT%"

if not exist ".venv\Scripts\python.exe" (
    py -3.13 -m venv .venv
    if errorlevel 1 exit /b 1
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1
python -m pip install -e ".[build,dev]"
if errorlevel 1 exit /b 1

python -m pytest
if errorlevel 1 exit /b 1
python -m ruff check src tests scripts whisper_transcriber.py
if errorlevel 1 exit /b 1
python -m ruff format --check src tests scripts whisper_transcriber.py
if errorlevel 1 exit /b 1

python -m PyInstaller --clean --noconfirm ^
    --distpath dist ^
    --workpath build\pyinstaller ^
    packaging\windows\tradutor_ao_vivo.spec
if errorlevel 1 exit /b 1

set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
    echo Inno Setup nao encontrado. Instale o Inno Setup 6 para gerar o instalador.
    exit /b 1
)

set "PROJECT_ROOT=%CD%"
"%ISCC%" packaging\windows\installer.iss
if errorlevel 1 exit /b 1

echo.
echo Aplicativo gerado em: dist\VoxNexo.exe
echo Instalador gerado em: dist\installer\Setup_VoxNexo.exe
echo Modelos de IA serao baixados gratuitamente na primeira execucao se ainda nao existirem.
popd
endlocal
