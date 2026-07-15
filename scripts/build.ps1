$ErrorActionPreference = "Stop"

python -m pip wheel . --no-deps --wheel-dir dist
exit $LASTEXITCODE
