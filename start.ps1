$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if (Test-Path ".venv\Scripts\python.exe") {
    & ".venv\Scripts\python.exe" run.py
} elseif (Test-Path "backend\.venv\Scripts\python.exe") {
    & "backend\.venv\Scripts\python.exe" run.py
} elseif (Test-Path "backend\venv\Scripts\python.exe") {
    & "backend\venv\Scripts\python.exe" run.py
} else {
    python run.py
}
