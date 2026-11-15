"""Verifica las trazas contra una nueva ejecución del motor C++."""
import json
import proyecto as p

def main():
    path=p.OUT/'trazas.json'
    if not path.exists():raise SystemExit('Primero ejecutar: python animacion_python/proyecto.py --prepare')
    if not p.exe_path().exists():p.compile_cpp()
    data=json.loads(path.read_text(encoding='utf-8'))
    for name,(n,edges) in p.CASES.items():
        stored=data[name]
        assert stored['n']==n and stored['edges']==[list(e) for e in edges],f'{name}: entrada desactualizada'
        actual=p.trace_case(n,edges)
        assert stored['events']==actual,f'{name}: eventos distintos del ejecutable actual'
        before=len(p.components(n,edges))
        expected=[v for v in range(n) if len(p.components(n,edges,v))>before]
        obtained=[v for v,cut in enumerate(actual[-1]['cut']) if cut]
        assert obtained==expected,f'{name}: resultado incorrecto'
        assert stored['components']==p.components(n,edges),f'{name}: componentes incorrectas'
        for v in range(n):
            assert stored['removals'][str(v)]==p.components(n,edges,v),f'{name}: eliminación incorrecta'
    print(f'OK: {len(data)} trazas verificadas contra C++ y conteo independiente de componentes.')

if __name__=='__main__':main()
