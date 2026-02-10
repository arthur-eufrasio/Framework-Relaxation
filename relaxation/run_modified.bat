REM Identifica o diretório onde o script está localizado
set "current_dir=%~dp0"

REM Caminho completo do arquivo .inp
set "input_file=%current_dir%backend\files\inp\ImplicitRelaxation_modified.inp"
set "job_dir=%current_dir%backend\files\job"
set "job_name=ImplicitRelaxation_modified"
echo Caminho do arquivo .inp: %input_file%

REM Verifica se o arquivo .inp existe
if exist "%input_file%" (
    REM Muda para o diretório do job
    cd /d "%job_dir%"

    REM Roda o job
    abaqus job=%job_name% input="%input_file%"

) else (
    echo O arquivo %input_file% não foi encontrado.
)

pause