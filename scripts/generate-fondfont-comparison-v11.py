"""Generate two new full MiniMax H3 studies, preserving every source and log."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v11'

def main():
 parser = argparse.ArgumentParser(description=__doc__)
 parser.add_argument('variant', choices=['playground','poetry'])
 parser.add_argument('--engine', type=Path, required=True)
 parser.add_argument('--model', type=Path, required=True)
 args = parser.parse_args()
 folder = ASSETS / args.variant
 out = folder / 'scene-h3.mp4'
 if out.exists(): parser.error('Preserve generations; choose a new version.')
 inputs = [folder/'start-anchor.png', folder/'end-anchor.png', folder/'h3-prompt.txt']
 command = [str(args.engine.resolve()), '-d', str(args.model.resolve()), '-p', inputs[2].read_text().strip(),
  '--width','768','--height','480','--render-width','512','--render-height','320',
  '--frames','65','--steps','20','--layers','50','--reuse','1','--ssd-streaming',
  '--seed',str(10062111 if args.variant == 'playground' else 10062112),
  '--first-frame',str(inputs[0]),'--last-frame',str(inputs[1]),'--profile','-o',str(out)]
 (folder/'generation.json').write_text(json.dumps({'engine':'MiniMax-H3','scope':'Original imagegen scene anchors; full-model physical prop motion. Verified real font outlines are composited afterward, never generated lettering.','command':command,'sources':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs]},indent=2)+'\n')
 with (folder/'generation.log').open('w') as log:
  subprocess.run(command,cwd=args.engine.resolve().parent,stdout=log,stderr=subprocess.STDOUT,check=True)
 print(out,flush=True)

if __name__ == '__main__': main()
