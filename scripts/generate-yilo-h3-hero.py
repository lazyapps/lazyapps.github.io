"""Animate our pelican pedaling illustration with the installed local MiniMax H3."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/yilo/marketing-v16'
ENGINE = Path('/Users/realazy/tmp/h3.c/h3')
MODEL = Path('/Users/realazy/.cache/huggingface/hub/models--MiniMaxAI--MiniMax-H3/snapshots/42ed227ee7df40d41602854ae760620d6eb651fe')
ANCHOR = ASSETS / 'pedaling-anchor.png'
OUTPUT = ASSETS / 'pedaling-h3.mp4'
PROMPT = '''An original colored straight-line hatching illustration on cream paper. Preserve the exact friendly white PELICAN riding the stationary bicycle at the LEFT. It is clearly a pelican: one long coral bill with a deep throat pouch, a gently curved long neck, a plump white feathered body, two small wings, exactly two legs and two coral webbed feet. Preserve the bill, pouch, head and body silhouette throughout. One near wing rests on the handlebar; the far wing is tucked. The pelican calmly pedals in one smooth continuous cycle. The two webbed feet stay attached to opposite pedals as the crank rotates clockwise evenly; each leg bends smoothly with unchanged thigh/shin lengths, hips remain on the saddle, no leg stretching. Keep near and far legs separate. Tiny gentle body sway, occasional soft blink. The bicycle is rigidly supported in the same place, perfectly round wheels rotate on fixed axles, frame and laptop stay unchanged. Fine teal, muted indigo, sage and coral hatching and sparse outlines; all hatch lines and paper remain stable. Locked camera, no pan, zoom, cut or scene change. Keep the entire background above the pelican and to its right as clean unmarked cream paper. No colored backdrop, filled patch, crosshatched background polygon, floating marks, dotted connectors or dashed lines. Keep upper quarter and right half empty for separately composited typography. No robot, human face, hands, fingers, extra limbs, extra birds, feathers appearing, warped beak, changing pouch, distorted wheels, foot sliding, dancing, flying, letters, captions, logos, speech bubbles, 3D or photorealism. Return naturally to the initial pose for a seamless loop. Silent.'''
if OUTPUT.exists():
    raise SystemExit(f'Preserve the existing generation: {OUTPUT}')
command = [str(ENGINE), '-d', str(MODEL), '-p', PROMPT,
    '--width','1280','--height','704','--render-width','640','--render-height','352',
    '--frames','65','--steps','20','--layers','50','--reuse','2','--ssd-streaming',
    '--seed','11072616','--first-frame',str(ANCHOR),'--last-frame',str(ANCHOR),'--profile','-o',str(OUTPUT)]
OUTPUT.with_suffix('.prompt.txt').write_text(PROMPT+'\n')
receipt = dict(model='MiniMax-H3',mode='local Apple Silicon first/last-frame inference',
    modelSnapshot=MODEL.name,engineSHA256=hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
    startedAt=datetime.now(timezone.utc).isoformat(),command=command,
    anchor=str(ANCHOR.relative_to(ROOT)),anchorSHA256=hashlib.sha256(ANCHOR.read_bytes()).hexdigest(),
    scope='Our original pelican line-art anchor with fixed-length legs and webbed feet. Model generates pelican/bicycle movement only. Exact localized text and app icon are composited separately.')
receipt_path = OUTPUT.with_suffix('.generation.json')
receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
with OUTPUT.with_suffix('.log').open('w') as log:
    subprocess.run(command,cwd=ENGINE.parent,stdout=log,stderr=subprocess.STDOUT,check=True)
receipt.update(completedAt=datetime.now(timezone.utc).isoformat(),outputSHA256=hashlib.sha256(OUTPUT.read_bytes()).hexdigest())
receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(OUTPUT,flush=True)
