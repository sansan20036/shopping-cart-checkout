$ErrorActionPreference = "Stop"

python -m compileall -q shopping_cart tests
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m unittest discover -s tests -v
exit $LASTEXITCODE
