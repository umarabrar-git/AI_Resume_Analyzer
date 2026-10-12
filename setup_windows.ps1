$ErrorActionPreference = "Stop"

# Run this script from any working directory; it resolves the project root.
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating the project's .venv virtual environment..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create .venv. Check that Python is installed and available as 'python'."
    }
}

Write-Host "Installing project dependencies into .venv..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "Could not upgrade pip in .venv."
}

& $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed. Review the pip error above before starting Flask."
}

& $VenvPython -c "import flask; print('Flask installed:', flask.__version__)"
if ($LASTEXITCODE -ne 0) {
    throw "Flask is still unavailable in .venv. Check the installation errors above."
}

Write-Host "Starting AI Resume Analyzer..."
& $VenvPython (Join-Path $ProjectRoot "app.py")
if ($LASTEXITCODE -ne 0) {
    throw "The app exited with an error. Review the traceback above."
}
