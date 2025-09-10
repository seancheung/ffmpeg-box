@echo off
setlocal enabledelayedexpansion

cd /D "%~dp0"

@REM load env
if exist env.txt (
    for /f "delims=" %%i in (env.txt) do set %%i
)

:venv
@REM check venv
if exist "%cd%\%venv_dir%" (
    call "%cd%\%venv_dir%\Scripts\activate.bat" || ( echo . && echo failed activate venv && goto :error )
    goto :install
)

@REM check uv
call uv --version || ( echo . && echo uv not found, checking conda && goto :conda )

@REM create venv
call uv venv --seed --python "%python_ver%" "%cd%\%venv_dir%" || ( echo . && echo failed to create venv && goto :error )
goto :venv

:conda
@REM check conda
call "%userprofile%\miniconda3\Scripts\activate.bat" "%userprofile%\miniconda3" || ( echo. && echo conda not found && goto :error )
( call conda deactivate && call conda deactivate && call conda deactivate ) 2>nul
if not exist "%cd%\%conda_dir%" (
	call conda create --no-shortcuts -y -k --prefix "%cd%\%conda_dir%" python=%python_ver% || ( echo. && echo failed to create conda env && goto :error )
)
call conda activate "%cd%\%conda_dir%" || ( echo. && echo conda env not found && goto :error )
echo conda env set to: %cd%\%conda_dir%

:install
@REM install deps
if not exist "%cd%\%installed_file%" (
	echo Installing dependencies...
	call pip install -r "%cd%\requirements.txt" || ( echo. && echo failed to install dependencies && goto :error )
	echo. 2>"%cd%\%installed_file%"
) else (
    echo "%installed_file%" already exists. Delete it to reinstall dependencies.
)

@REM run
call python run.py || ( echo. && echo failed to start app && goto :error )

:end
exit /b 0

:error
pause