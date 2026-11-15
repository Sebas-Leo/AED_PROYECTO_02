"""Empaqueta solamente el código y los recursos de creación del video."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parent
target=ROOT/'animacion_python/output/Proyecto_Video_Articulaciones.zip'
with ZipFile(target,'w',ZIP_DEFLATED) as package:
    candidates=[ROOT/'README.md',ROOT/'empaquetar.py',ROOT/'ejecutar.ps1',ROOT/'.gitignore',ROOT/'.gitattributes']
    for directory in ('implementacion_cpp','animacion_python'):
        candidates.extend((ROOT/directory).rglob('*'))
    for path in sorted(candidates):
        if not path.is_file():continue
        rel=path.relative_to(ROOT)
        if any(p in ('build','__pycache__','.venv','frames') for p in rel.parts):continue
        if path.suffix.lower() in ('.zip','.wav','.mp3','.m4a','.pdf'):continue
        package.write(path,Path('proyecto_02')/rel)
print(target)
