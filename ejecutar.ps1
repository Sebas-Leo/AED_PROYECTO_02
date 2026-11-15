param([ValidateSet('all','prepare','video','test')][string]$Accion='all')
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskPython=$null
$taskBundled=Get-ChildItem -Path 'C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime*\dependencies\python\python.exe' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($env:VIRTUAL_ENV -and (Test-Path -LiteralPath (Join-Path $env:VIRTUAL_ENV 'Scripts\python.exe'))) { $taskPython=Join-Path $env:VIRTUAL_ENV 'Scripts\python.exe' }
elseif ($taskBundled) { $taskPython=$taskBundled.FullName }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $taskPython=(Get-Command python).Source }
elseif (Get-Command py -ErrorAction SilentlyContinue) { $taskPython=(Get-Command py).Source }
else { throw 'Instala Python 3.10 o superior.' }
if ($Accion -eq 'test') { & $taskPython implementacion_cpp/tests/test_articulaciones.py }
else { & $taskPython animacion_python/proyecto.py "--$Accion" }
if ($LASTEXITCODE -ne 0) { throw 'El proceso falló. Revisa el mensaje anterior.' }
