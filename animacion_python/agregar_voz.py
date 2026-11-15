"""Mezcla una narración ya sincronizada con el video de 180 segundos."""
from pathlib import Path
import argparse, json, shutil, subprocess
ROOT=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('audio',type=Path,help='WAV, MP3 o M4A con la narración completa')
    args=ap.parse_args();audio=args.audio.resolve()
    if not audio.is_file():ap.error('No existe el archivo de voz indicado.')
    ffmpeg=shutil.which('ffmpeg');probe=shutil.which('ffprobe')
    if not ffmpeg or not probe:ap.error('FFmpeg y ffprobe deben estar en el PATH.')
    result=subprocess.run([probe,'-v','error','-show_entries','format=duration','-of','json',str(audio)],capture_output=True,text=True,check=True)
    duration=float(json.loads(result.stdout)['format']['duration'])
    if duration>180.1:ap.error(f'La narración dura {duration:.1f} s. Ajústala a 180 s como máximo; no se recortará automáticamente.')
    source=ROOT/'output/articulaciones_sin_voz.mp4'
    if not source.exists():ap.error('Primero genera el video con python proyecto.py --video.')
    target=ROOT/'output/articulaciones_con_voz.mp4'
    subprocess.run([ffmpeg,'-y','-i',str(source),'-i',str(audio),'-map','0:v:0','-map','1:a:0',
      '-c:v','copy','-c:a','aac','-b:a','192k','-af','apad','-t','180','-movflags','+faststart',str(target)],check=True)
    print(f'Video final: {target}')

if __name__=='__main__':main()
