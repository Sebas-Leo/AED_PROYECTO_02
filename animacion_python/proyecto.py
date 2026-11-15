"""Pipeline reproducible: C++ -> traza JSON -> animacion -> MP4.

Uso: python proyecto.py --all | --prepare | --video
No contiene una lista prefijada de articulaciones: todo resultado y tabla
proviene del ejecutable C++ compilado desde implementacion_cpp/articulaciones.cpp.
"""
from pathlib import Path
import argparse, json, math, os, shutil, subprocess, sys, textwrap
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
CPP=ROOT.parent/'implementacion_cpp'
OUT=ROOT/'output'; BUILD=CPP/'build'; FRAMES=OUT/'frames'
W,H=1920,1080
BG='#0B1220'; PANEL='#121E30'; WHITE='#F0F5FC'; MUTED='#9BACC3'
CYAN='#54DBE0'; GOLD='#FFC46B'; CORAL='#FF7986'; LINE='#41536D'; GREEN='#8EE0B2'
CASES={
 'principal':(7,[(0,1),(1,2),(2,0),(1,3),(3,4),(4,5),(5,3),(5,6)]),
 'raiz':(3,[(0,1),(0,2)]),
 'aislado':(1,[]),
 'desconectado':(6,[(0,1),(1,2),(3,4)]),
 'vacio':(0,[]),
}
SCENES=[(0,12,'ARTICULACIONES','Un vértice puede sostener toda una red.'),
 (12,30,'01 / QUÉ SON','Eliminar un vértice puede aumentar las componentes.'),
 (30,50,'02 / LA IDEA DEL DFS','tin: descubrimiento · low: conexión más antigua'),
 (50,70,'03 / LA CONDICIÓN','¿El subárbol tiene una salida hacia un ancestro?'),
 (70,125,'04 / EJECUCIÓN REAL','Cada estado viene del programa en C++.'),
 (125,145,'05 / CASOS BORDE','La raíz tiene su propia regla.'),
 (145,163,'06 / COSTO Y USO','Una sola búsqueda en profundidad.'),
 (163,180,'ANIMA TU ALGORITMO','Articulaciones · CS2023 · Proyecto 2')]

def run(args,**kw):
    return subprocess.run([str(x) for x in args],check=True,**kw)

def exe_path():return BUILD/('articulaciones.exe' if os.name=='nt' else 'articulaciones')

def compile_cpp():
    BUILD.mkdir(exist_ok=True);OUT.mkdir(exist_ok=True)
    compiler=shutil.which('g++') or shutil.which('clang++')
    if not compiler:raise RuntimeError('Instala g++ o clang++ con soporte C++17 y agrégalo al PATH.')
    run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-pedantic',CPP/'articulaciones.cpp','-o',exe_path()])

def graph_input(n,edges):return f'{n} {len(edges)}\n'+''.join(f'{u} {v}\n' for u,v in edges)

def trace_case(n,edges):
    result=run([exe_path(),'--trace'],input=graph_input(n,edges),capture_output=True,text=True)
    return [json.loads(line) for line in result.stdout.splitlines()]

def components(n,edges,removed=-1):
    # Independiente del algoritmo low-link; sirve para explicar la eliminación.
    adj=[[] for _ in range(n)]
    for u,v in edges:
        if removed not in (u,v):adj[u].append(v);adj[v].append(u)
    seen={removed};groups=[]
    for v in range(n):
        if v in seen:continue
        stack=[v];seen.add(v);group=[]
        while stack:
            x=stack.pop();group.append(x)
            for y in adj[x]:
                if y not in seen:seen.add(y);stack.append(y)
        groups.append(group)
    return groups

def prepare():
    compile_cpp(); data={}
    (CPP/'examples').mkdir(exist_ok=True)
    for name,(n,edges) in CASES.items():
        events=trace_case(n,edges)
        data[name]={'n':n,'edges':edges,'events':events,'components':components(n,edges),
                    'removals':{str(v):components(n,edges,v) for v in range(n)}}
        (CPP/'examples'/f'{name}.txt').write_text(graph_input(n,edges),encoding='utf-8')
    (OUT/'trazas.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Compilación y trazas reales listas.',flush=True)
    return data

@lru_cache(None)
def font(size,bold=False,mono=False):
    candidates=([r'C:/Windows/Fonts/consola.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'] if mono else
      ([r'C:/Windows/Fonts/segoeuib.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'] if bold else
       [r'C:/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']))
    for path in candidates:
        if Path(path).exists():return ImageFont.truetype(path,size)
    return ImageFont.load_default(size=size)

def txt(draw,xy,text,size=32,color=WHITE,bold=False,mono=False):
    draw.text(xy,text,font=font(size,bold,mono),fill=color)

def lines(draw,xy,text,width=48,size=32,color=MUTED,bold=False,gap=12):
    x,y=xy
    for paragraph in text.split('\n'):
        for line in textwrap.wrap(paragraph,width=width) or ['']:
            txt(draw,(x,y),line,size,color,bold);y+=size+gap
    return y

def card(d,box,fill=PANEL):d.rounded_rectangle(box,radius=24,fill=fill)

def graph(d,case,event=None,remove=-1,group_colors=False,kind='principal',phase=0):
    if kind=='principal':pos=[(210,420),(440,290),(440,610),(710,425),(960,290),(960,600),(1150,650)]
    elif kind=='raiz':pos=[(650,350),(450,610),(850,610)]
    else:pos=[(650,470)]
    cut=event['cut'] if event else [0]*case['n']
    visited=event['tin'] if event else [-1]*case['n']
    palette=[CYAN,GOLD,GREEN,CORAL];colors={}
    if group_colors:
        for i,g in enumerate(case['removals'][str(remove)]):
            for v in g:colors[v]=palette[i%len(palette)]
    for u,v in case['edges']:
        a,b=pos[u],pos[v];c=LINE;width=6
        if remove in (u,v):c='#243043';width=3
        elif group_colors:c=colors[u]
        elif event and event['v']>=0 and event['to']>=0 and event['kind'] not in ('root','result') and {u,v}=={event['v'],event['to']}:
            c=GOLD if event['kind']=='back' else CYAN;width=10
        d.line([a,b],fill=c,width=width)
    for v,(x,y) in enumerate(pos):
        c=colors.get(v, CORAL if cut[v] else CYAN if visited[v]>=0 else MUTED)
        if v==remove:c='#41536D'
        radius=39
        if event and event['v']==v:
            pulse=50+int(5*math.sin(phase*math.pi*2))
            d.ellipse((x-pulse,y-pulse,x+pulse,y+pulse),outline=CYAN,width=3)
        d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=BG,outline=c,width=6)
        txt(d,(x-12,y-26),str(v),38,c,True)
        if v==remove:
            d.line((x-28,y-28,x+28,y+28),fill=CORAL,width=6)
            d.line((x-28,y+28,x+28,y-28),fill=CORAL,width=6)
    if event and event['kind'] in ('tree','back','return') and event['v']>=0 and event['to']>=0:
        a,b=pos[event['v']],pos[event['to']]
        if event['kind']=='return':a,b=b,a
        q=phase%1;x=a[0]+(b[0]-a[0])*q;y=a[1]+(b[1]-a[1])*q
        d.ellipse((x-9,y-9,x+9,y+9),fill=GOLD)

def table(d,event,n=7):
    card(d,(1270,230,1848,788));txt(d,(1300,251),'ESTADO DEL PROGRAMA',25,CYAN,True)
    for x,t in [(1300,'v'),(1380,'tin'),(1510,'low'),(1640,'¿corte?')]:txt(d,(x,307),t,27,MUTED,True)
    for v in range(n):
        y=363+53*v
        if event['v']==v:d.rounded_rectangle((1290,y-5,1825,y+44),radius=8,fill='#203349')
        vals=[str(v),str(event['tin'][v]) if event['tin'][v]>=0 else '—',str(event['low'][v]) if event['low'][v]>=0 else '—','SÍ' if event['cut'][v] else '—']
        for x,value in zip([1300,1380,1510,1660],vals):txt(d,(x,y),value,30,CORAL if event['cut'][v] else WHITE,mono=True)

def event_text(e):
    v,to=e['v'],e['to'];kind=e['kind']
    if kind=='discover':return f'Descubrimos {v}: tin[{v}] = low[{v}] = {e["tin"][v]}.'
    if kind=='tree':return f'Arista de árbol: DFS avanza de {v} a {to}.'
    if kind=='back':return f'Arista ya visitada: low[{v}] = min(low[{v}], tin[{to}]) = {e["low"][v]}.'
    if kind=='return':return f'Regreso de {to}: low[{v}] = min(low[{v}], low[{to}]) = {e["low"][v]}.'
    if kind=='cut':return f'low[{to}] = {e["low"][to]} >= tin[{v}] = {e["tin"][v]}: {v} es articulación.'
    if kind=='root':return f'Raíz {v}: {to} hijo(s) DFS. '+('Es articulación.' if e['cut'][v] else 'No es articulación.')
    if kind=='finish':return f'Termina DFS({v}). Se devuelve low[{v}] = {e["low"][v]}.'
    found=', '.join(str(i) for i,c in enumerate(e['cut']) if c)
    return f'Resultado calculado: articulaciones = {{{found}}}.'

def paint(t,data,config):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    scene=next((s for s in SCENES if s[0]<=t<s[1]),SCENES[-1]);start,end,title,sub=scene
    txt(d,(74,45),'CS2023 / ALGORITMOS Y ESTRUCTURAS DE DATOS',24,MUTED,True)
    txt(d,(74,94),title,55,WHITE,True);txt(d,(78,170),sub,29,MUTED)
    d.line((78,222,1845,222),fill=LINE,width=2)
    main=data['principal'];events=main['events'];last=events[-1]
    if start==0:
        graph(d,main,last)
        txt(d,(1280,325),'PUNTOS',52,WHITE,True);txt(d,(1280,390),'CRÍTICOS',64,CORAL,True)
        lines(d,(1280,500),'¿Qué pasa si uno de estos vértices desaparece?',width=23,size=34)
        txt(d,(1280,685),'DFS + tin + low',32,CYAN,True)
        card(d,(80,810,1840,958));txt(d,(112,842),'Una implementación real. Una explicación visual.',43,WHITE,True)
    elif start==12:
        removed=1 if t>=20 else -1
        graph(d,main,remove=removed,group_colors=removed>=0)
        card(d,(1270,275,1848,751))
        count=len(main['components']) if removed<0 else len(main['removals'][str(removed)])
        txt(d,(1310,320),'COMPONENTES',32,MUTED,True);txt(d,(1310,370),str(count),110,CYAN,True)
        lines(d,(1310,520),'Red original' if removed<0 else 'Al quitar el vértice 1, la red se separa.',width=24,size=32)
        lines(d,(100,835),'Una articulación es un vértice cuya eliminación, junto con sus aristas, aumenta el número de componentes conexas.',width=90,size=34,color=WHITE)
    elif start==30:
        # Una instantánea real después de procesar la arista 2 -> 0.
        e=next(e for e in events if e['kind']=='back' and e['v']==2 and e['to']==0)
        graph(d,main,e,phase=t%1);table(d,e)
        card(d,(80,815,1840,970))
        txt(d,(110,838),'tin[v] = momento en que descubrimos v.',34,CYAN,True)
        txt(d,(110,891),'low[v] = menor tin alcanzable desde su subárbol con hasta una arista de retorno.',31,WHITE)
    elif start==50:
        e=next(e for e in events if e['kind']=='cut' and e['v']==3)
        graph(d,main,e,phase=t%1);table(d,e)
        card(d,(80,815,1840,970));txt(d,(110,835),'Si v NO es raíz: low[hijo] >= tin[v]  →  v es articulación.',37,CORAL,True)
        txt(d,(110,900),'La igualdad también cuenta: volver a v no permite esquivar v.',32,WHITE)
    elif start==70:
        idx=min(len(events)-1,int((t-70)/55*len(events)));e=events[idx]
        graph(d,main,e,phase=((t-70)/55*len(events))%1);table(d,e)
        txt(d,(1285,808),f'EVENTO {idx+1:02d} / {len(events):02d}',25,CYAN,True)
        card(d,(80,865,1840,975));lines(d,(110,883),event_text(e),width=100,size=32,color=WHITE,gap=6)
        # Indicador de avance continuo: la estructura y los valores son de la traza.
        progress=((t-70)/55*len(events))%1
        d.rounded_rectangle((1280,855,1280+max(2,int(550*progress)),862),radius=3,fill=CYAN)
    elif start==125:
        which='raiz' if t<136 else 'aislado';case=data[which];e=case['events'][-1]
        graph(d,case,e,kind=which)
        card(d,(1270,275,1848,760))
        if which=='raiz':
            txt(d,(1310,310),'RAÍZ DEL DFS',34,GOLD,True)
            lines(d,(1310,385),'Es articulación si tiene más de un hijo en el árbol DFS.',width=24,size=34,color=WHITE)
            txt(d,(1310,625),'0 tiene 2 hijos.',33,CORAL,True)
        else:
            txt(d,(1310,310),'UN SOLO VÉRTICE',31,GOLD,True)
            lines(d,(1310,385),'Al eliminarlo, pasamos de 1 componente a 0. No aumenta.',width=24,size=34,color=WHITE)
            txt(d,(1310,650),'No es articulación.',30,CYAN,True)
        txt(d,(110,850),'En grafos desconectados iniciamos un DFS por componente.',35,WHITE,True)
        txt(d,(110,912),'Un grafo vacío tampoco tiene articulaciones.',30,MUTED)
    elif start==145:
        card(d,(80,285,1180,780));txt(d,(125,330),'O(|V| + |E|)',100,CYAN,True)
        txt(d,(130,490),'TIEMPO DEL ALGORITMO',29,MUTED,True)
        txt(d,(130,560),'Cada vértice se descubre una vez.',35,WHITE)
        txt(d,(130,625),'Cada arista se examina en ambos sentidos.',33,WHITE)
        txt(d,(130,695),'Espacio: O(|V| + |E|), incluida la adyacencia.',30,GOLD)
        card(d,(1230,285,1848,780));txt(d,(1270,330),'¿PARA QUÉ?',39,CORAL,True)
        lines(d,(1270,420),'Detectar puntos de falla en redes, conexiones y sistemas de comunicación.',width=25,size=34,color=WHITE)
        lines(d,(100,845),'La traza didáctica y el render agregan trabajo; no forman parte del costo del algoritmo sin instrumentación.',width=94,size=30)
    else:
        result=', '.join(str(i) for i,c in enumerate(last['cut']) if c)
        txt(d,(100,285),'RESULTADO: '+result,57,CORAL,True)
        txt(d,(100,385),'DFS descubre. low conecta. La condición detecta.',40,WHITE,True)
        for i,name in enumerate(config['integrantes']):txt(d,(105,510+i*72),name,40,WHITE)
        txt(d,(105,805),'Implementación: C++17  /  Animación: Python + Pillow + FFmpeg',28,CYAN)
        txt(d,(105,866),'Referencia conceptual: cp-algorithms.com/graph/cutpoints.html',25,MUTED)
    d.rectangle((0,1032,W,1080),fill=PANEL)
    txt(d,(78,1040),'ARTICULACIONES / PROYECTO 2',20,MUTED,True)
    txt(d,(1655,1039),f'{int(t)//60:02d}:{int(t)%60:02d} / 03:00',22,MUTED,mono=True)
    d.rectangle((0,1027,max(1,int(W*t/180)),1032),fill=CYAN)
    return im

def snapshots(data,config):
    FRAMES.mkdir(parents=True,exist_ok=True)
    for name,t in [('portada',2),('definicion',24),('low',40),('condicion',58),('ejecucion',119),('raiz',130),('aislado',140),('complejidad',150),('creditos',170)]:
        paint(t,data,config).save(FRAMES/f'{name}.png')

def render_video(data,config):
    ffmpeg=shutil.which('ffmpeg')
    if not ffmpeg:raise RuntimeError('Instala FFmpeg y agrégalo al PATH.')
    # 12 estados visuales por segundo; salida MP4 a 24 fps, 1080p, H.264.
    # No se animan resultados inventados: la secuencia viene de las trazas.
    target=OUT/'articulaciones_sin_voz.mp4'
    command=[ffmpeg,'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24',
       '-s',f'{W}x{H}','-r','12','-i','-','-an','-c:v','libx264','-preset','fast','-crf','20',
       '-pix_fmt','yuv420p','-r','24','-movflags','+faststart',str(target)]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for i in range(180*12):
            proc.stdin.write(paint(i/12,data,config).tobytes())
            if i%(12*15)==0:print(f'Render: {i//12:3d} / 180 s',flush=True)
        proc.stdin.close()
        if proc.wait()!=0:raise RuntimeError('FFmpeg no pudo renderizar el video.')
    except BaseException:
        proc.kill();proc.wait();raise
    print(f'Video listo: {target}',flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--all',action='store_true');ap.add_argument('--prepare',action='store_true');ap.add_argument('--video',action='store_true');args=ap.parse_args()
    config=json.loads((ROOT/'config.json').read_text(encoding='utf-8'))
    if args.all or args.prepare or not (OUT/'trazas.json').exists():data=prepare()
    else:data=json.loads((OUT/'trazas.json').read_text(encoding='utf-8'))
    snapshots(data,config)
    if args.all or args.video:render_video(data,config)
    if not any(vars(args).values()):ap.print_help()

if __name__=='__main__':main()
