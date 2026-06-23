@echo off
setlocal enabledelayedexpansion

REM Identifica o diretório
set "current_dir=%~dp0"
set "input_file=%current_dir%backend\files\inp\ImplicitRelaxation.inp"
set "input_file_modified=%current_dir%backend\files\inp\ImplicitRelaxation_modified.inp"
set "job_dir=%current_dir%backend\files\job"
set "job_name=ImplicitRelaxation_modified"

echo Caminho do arquivo .inp: %input_file%

REM Verifica se o arquivo existe
if exist "%input_file%" (
    echo Executando script Python...
    python "%current_dir%inp_modifier_initial_conditions.py" || (
        echo ERRO: O script Python falhou.
        pause
        exit /b
    )

    REM Muda para o diretório do job
    echo Indo para o diretorio do job...
    cd /d "%job_dir%" || (
        echo ERRO: Nao foi possivel acessar %job_dir%
        pause
        exit /b
    )

    REM Roda o job com log de erro para tela
    echo Iniciando o Job do Abaqus...
    call abaqus job=%job_name% input="%input_file_modified%"
    
    if errorlevel 1 (
        echo ERRO: O comando Abaqus falhou. Verifique se o caminho do abaqus esta no PATH do Windows.
    ) else (
        echo Job iniciado com sucesso.
    )

) else (
    echo ERRO: O arquivo %input_file% nao foi encontrado.
)

echo.
echo Execucao finalizada. Pressione qualquer tecla para fechar.
pause