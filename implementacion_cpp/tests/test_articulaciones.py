"""Pruebas de caja negra contra conteo independiente de componentes."""
from pathlib import Path
import argparse, itertools, random, subprocess, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'animacion_python'))
import proyecto as p

def oracle(n,edges):
    before=len(p.components(n,edges))
    return [v for v in range(n) if len(p.components(n,edges,v))>before]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable',type=Path,help='Ejecutable ya compilado, por ejemplo mediante CMake')
    args=parser.parse_args()
    if args.executable:
        executable=args.executable.resolve()
        if not executable.is_file():parser.error('No existe el ejecutable indicado.')
        p.exe_path=lambda: executable
    if not p.exe_path().exists():p.compile_cpp()
    cases=list(p.CASES.values())
    for n in range(5):
        possible=list(itertools.combinations(range(n),2))
        for mask in range(1<<len(possible)):
            cases.append((n,[e for i,e in enumerate(possible) if mask>>i&1]))
    rng=random.Random(2026)
    for _ in range(220):
        n=rng.randint(1,9)
        edges=[(u,v) for u in range(n) for v in range(u,n) if rng.random()<.24]
        if edges and rng.random()<.5:edges.append(rng.choice(edges))
        rng.shuffle(edges);cases.append((n,edges))
    for i,(n,edges) in enumerate(cases):
        result=subprocess.run([str(p.exe_path())],input=p.graph_input(n,edges),capture_output=True,text=True,check=True)
        actual=list(map(int,result.stdout.split()));expected=oracle(n,edges)
        assert actual==expected,(i,n,edges,actual,expected)
    for name,(n,edges) in p.CASES.items():
        events=p.trace_case(n,edges)
        assert events[-1]['kind']=='result'
        assert [v for v,c in enumerate(events[-1]['cut']) if c]==oracle(n,edges)
        for e in events:
            for v in range(n):
                assert e['low'][v]<=e['tin'][v] if e['tin'][v]>=0 else e['low'][v]==-1
    result=f'OK: {len(cases)} grafos comparados con oraculo independiente.\nOK: trazas de los {len(p.CASES)} ejemplos coherentes.\nSemilla aleatoria: 2026. Incluye vacio, aislados, desconectados, lazos y aristas paralelas.\n'
    p.OUT.mkdir(exist_ok=True);(p.OUT/'validacion.txt').write_text(result,encoding='utf-8');print(result)

if __name__=='__main__':main()
