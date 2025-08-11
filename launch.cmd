@echo off
setlocal enabledelayedexpansion

cd /D "%~dp0"

@rem test the conda binary
echo Miniconda version:

call conda --version || (call %userprofile%\miniconda3\Scripts\activate.bat %userprofile%\miniconda3) || ( echo. && echo Miniconda not found. && goto end )

@rem deactivate existing conda envs as needed to avoid conflicts
(call conda deactivate && call conda deactivate && call conda deactivate) 2>nul

set CONDA_DIR=%cd%\.conda
set PYTHON_VER=3.11

@rem create the installer env
if not exist "%CONDA_DIR%" (
	echo Packages to install: %PACKAGES_TO_INSTALL%
	call conda create --no-shortcuts -y -k --prefix "%CONDA_DIR%" python=%PYTHON_VER% || ( echo. && echo Conda environment creation failed. && goto end )
)

@rem environment isolation
set PYTHONNOUSERSITE=1
set PYTHONPATH=
set PYTHONHOME=

@rem activate installer env
call conda activate "%CONDA_DIR%" || ( echo. && echo Miniconda env not found. && goto end )
echo Conda env set to: %CONDA_PREFIX%

set INIT_LOCKFILE=%cd%\.lock
if not exist "%INIT_LOCKFILE%" (
	echo Installing dependencies...
	call pip install -r "requirements.txt"
	echo. 2>"%INIT_LOCKFILE%"
)

@rem launch
call python -s run.py
@REM call gradio run.py --demo-name=app

:end
pause