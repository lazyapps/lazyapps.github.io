"""Generate genuine full-model MiniMax-H3 truck transport for the foundry film."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'scripts/assets/fondfont/animation/v13'

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',type=Path,required=True)
 p.add_argument('--model',type=Path,required=True)
 a=p.parse_args(); out=ASSETS/'transport-h3.mp4'
 if out.exists(): p.error('Preserve generation; choose a new version.')
 inputs=[ASSETS/name for name in ('start-anchor.png','end-anchor.png','h3-prompt.txt')]
 command=[str(a.engine.resolve()),'-d',str(a.model.resolve()),'-p',inputs[2].read_text().strip(),'--width','768','--height','480','--render-width','512','--render-height','320','--frames','65','--steps','20','--layers','50','--reuse','1','--ssd-streaming','--seed','10061313','--first-frame',str(inputs[0]),'--last-frame',str(inputs[1]),'--profile','-o',str(out)]
 (ASSETS/'generation.json').write_text(json.dumps({'engine':'MiniMax-H3','scope':'A newly generated complete truck journey. Fonts, accurate words and synchronized foundry/loading mechanics are separate native compositing. Empty-truck return reuses only the physical journey in reverse, not production or unloading.','command':command,'sources':[{'path':str(s.relative_to(ROOT)),'sha256':hashlib.sha256(s.read_bytes()).hexdigest()} for s in inputs]},ensure_ascii=False,indent=2)+'\n')
 with (ASSETS/'generation.log').open('w') as log:
  subprocess.run(command,cwd=a.engine.resolve().parent,stdout=log,stderr=subprocess.STDOUT,check=True)
 print(out,flush=True)

if __name__=='__main__': main()
