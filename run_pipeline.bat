@echo off
setlocal enabledelayedexpansion

:: ==============================================================================
:: Automated Pipeline: ODB Extraction -> Model Creation -> Relaxation Simulation
:: ==============================================================================

echo ==============================================================================
echo [START] Relaxation Framework - Full Pipeline
echo ==============================================================================

:: Verify configuration files exist
if not exist "config\model_config.json" (
    echo [ERROR] Configuration file 'config\model_config.json' not found.
    goto :error
)

if not exist "config\odb_config.json" (
    echo [ERROR] Configuration file 'config\odb_config.json' not found.
    goto :error
)

:: ------------------------------------------------------------------------------
:: Step 1: Pre-run Cleanup
:: ------------------------------------------------------------------------------
echo.
echo ==============================================================================
echo [STEP 1/4] Cleaning previous temporary files...
echo ==============================================================================
if exist "extraction\utilities\clean_files.py" (
    python extraction\utilities\clean_files.py
)
if exist "relaxation\utilities\clean_files.py" (
    python relaxation\utilities\clean_files.py
)

:: ------------------------------------------------------------------------------
:: Step 2: Extraction from Source ODB
:: ------------------------------------------------------------------------------
echo.
echo ==============================================================================
echo [STEP 2/4] Extracting results from ODB...
echo ==============================================================================
python extraction\main.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] ODB extraction failed with exit code %ERRORLEVEL%.
    goto :error
)
echo [SUCCESS] Extraction completed successfully.

:: ------------------------------------------------------------------------------
:: Step 3: Base Model Creation
:: ------------------------------------------------------------------------------
echo.
echo ==============================================================================
echo [STEP 3/4] Creating base model (relaxation\main.py)...
echo ==============================================================================
python relaxation\main.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Model creation failed with exit code %ERRORLEVEL%.
    goto :error
)
echo [SUCCESS] Base model created and input file generated.

:: ------------------------------------------------------------------------------
:: Step 4: Apply Initial Conditions and Run Relaxation Simulation
:: ------------------------------------------------------------------------------
echo.
echo ==============================================================================
echo [STEP 4/4] Applying initial conditions and running simulation (run_modified.bat)...
echo ==============================================================================
if not exist "relaxation\run_modified.bat" (
    echo [ERROR] Script 'relaxation\run_modified.bat' not found.
    goto :error
)

call relaxation\run_modified.bat
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Relaxation simulation failed with exit code %ERRORLEVEL%.
    goto :error
)
echo [SUCCESS] Relaxation simulation finished successfully.

:: ------------------------------------------------------------------------------
:: Pipeline Success
:: ------------------------------------------------------------------------------
echo.
echo ==============================================================================
echo [COMPLETED] Full pipeline executed successfully!
echo ==============================================================================
pause
exit /b 0

:error
echo.
echo ==============================================================================
echo [FAILED] Pipeline terminated with errors. Please check the logs above.
echo ==============================================================================
pause
exit /b 1