"""Render the original 12-language hatched-line Yilo hero and provenance."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from lib.yilo_wheel_supports import wheel_support_filter

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'video/yilo-hero'
PUBLIC = ROOT / 'public/v/yilo'
CACHE = ROOT / '.build/yilo-hero-v22'
MANIFEST = ROOT / 'scripts/assets/yilo/hero-video-source.json'
COPY = json.loads((ROOT / 'src/i18n/yilo-hero-copy.json').read_text())
VERSION = 'v22'
END_HOLD_FRAME = json.loads((PROJECT/'src/timing.json').read_text())['endHoldStartFrame']
TITLE = 'Yilo — 边蹬边学 / ' + COPY['en']['lineTitle']
COMMENT = 'Native Yilo RecordCardView captures with short AI-agent input, the largest app text setting, Pinyin and Romaji. Original pelican line art animated locally with MiniMax H3. Learning helps more natural conversations with people. Formerly YiYan. Isolated native component samples, not a live app recording.'
BROWSER = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--locales', nargs='+', choices=list(COPY), default=list(COPY))
parser.add_argument('--retitle-only', action='store_true', help='Update movie title metadata without re-encoding its picture or sound')
parser.add_argument('--remove-wheel-supports-only', action='store_true', help='Clean completed v19 exports while preserving their timing and audio')
args = parser.parse_args()
PUBLIC.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)

def run(command):
    subprocess.run([str(arg) for arg in command], cwd=PROJECT, check=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

previous = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
if previous and previous.get('version') != VERSION:
    archive = ROOT / f'.build/yilo-film-receipts/previous-{previous["version"]}-hero-source.json'
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        shutil.copy2(MANIFEST, archive)
outputs = {item['locale']: item for item in previous.get('outputs', [])}
postprocess_inputs = [ROOT/path for path in previous.get('wheelSupportRemoval', {}).get('inputs', [])] if previous.get('version') == VERSION and args.retitle_only else []
def publish():
    source_files = [ROOT/'src/i18n/yilo-art-copy.json',ROOT/'src/i18n/yilo-examples.json',ROOT/'scripts/generate-yilo-h3-hero.py',ROOT/'src/i18n/yilo-hero-copy.json',Path(__file__),ROOT/'scripts/assets/yilo/hero-music-credits.txt',ROOT/'scripts/prepare-yilo-hero-music.py',ROOT/'scripts/assets/yilo/audio/source.json',ROOT/'scripts/assets/yilo/audio/fluffing-a-duck.mp3']
    source_files += [ROOT/'scripts/assets/yilo/hero-native-source.json',ROOT/'scripts/capture-yilo-hero-screenshots.py',ROOT/'scripts/assets/yilo/capture/YiloHeroCapture.swift',ROOT/'scripts/assets/yilo/capture/hero-record-en.json',ROOT/'scripts/assets/yilo/capture/hero-record-zh.json']
    source_files += [ROOT/item['source'] for item in json.loads((ROOT/'scripts/assets/yilo/hero-native-source.json').read_text())['captures']]
    source_files += list((ROOT/'scripts/assets/yilo/capture/hero-records').glob('*.json'))
    source_files += [path for path in PROJECT.rglob('*') if path.is_file() and 'node_modules' not in path.parts and '.git' not in path.parts and path.suffix in ('.tsx','.ts','.json','.yaml','.png','.wav','.mp4')]
    source_files += [path for path in (ROOT/'scripts/assets/yilo/marketing-v16').iterdir() if path.is_file() and path.suffix in ('.png','.mp4','.json','.txt')]
    source_files += [ROOT/'scripts/lib/yilo_wheel_supports.py', *postprocess_inputs]
    temporary = MANIFEST.with_suffix('.tmp')
    temporary.write_text(json.dumps(dict(version=VERSION,checkedOn=datetime.now().astimezone().date().isoformat(),style='original-straight-hatched-line-illustration-local-h3',
        generation=dict(model='MiniMax-H3',mode='local Apple Silicon first/last-frame inference',receipt='scripts/assets/yilo/marketing-v16/pedaling-h3.generation.json'),
        reference='https://x.com/pmamtraveller/status/2118294851431092442',referenceUse='Visual style study only; no reference illustration copied into the film.',
        nativeRecordSource='scripts/assets/yilo/hero-native-source.json',musicSource='scripts/assets/yilo/audio/source.json',metadata=dict(title=TITLE,comment=COMMENT),sources={str(path.relative_to(ROOT)):sha(path) for path in sorted(set(source_files))},
        wheelSupportRemoval=dict(filter=wheel_support_filter(),mode='existing-v19-exports' if postprocess_inputs else 'composed-exports',inputs=[str(path.relative_to(ROOT)) for path in postprocess_inputs]),
        ending=dict(holdStartFrame=END_HOLD_FRAME,holdFrames=336-END_HOLD_FRAME,seconds=(336-END_HOLD_FRAME)/24,fadeToBlank=False),
        renderedCopy={tag:{key:value[key] for key in ['reuse']} for tag,value in COPY.items()},outputs=[outputs[tag] for tag in COPY if tag in outputs]),ensure_ascii=False,indent=2)+'\n')
    temporary.replace(MANIFEST)

if args.remove_wheel_supports_only:
    assert VERSION == 'v20', 'The v19 upgrade is historical; render the current composition instead'
    assert previous.get('version') == 'v19', 'Clean the reviewed v19 exports once'
    assert set(args.locales) == set(COPY), 'Update every locale together'
    changed_sources = {'src/i18n/yilo-hero-copy.json', str(Path(__file__).relative_to(ROOT)), 'video/yilo-hero/src/YiloLineHero.tsx'}
    for tag, fields in previous['renderedCopy'].items():
        assert all(COPY[tag][key] == value for key, value in fields.items()), 'Burned-in copy changed; render the film'
    for path, expected in previous['sources'].items():
        if path not in changed_sources:
            assert sha(ROOT/path) == expected, f'Other movie source changed: {path}'
    postprocess_inputs.append(archive)
    for locale in args.locales:
        item = outputs[locale]
        original = ROOT/item['video']['path']
        assert sha(original) == item['video']['sha256'], 'Original export changed'
        postprocess_inputs.append(original)
        video = PUBLIC/f'hero-{locale}-{VERSION}.mp4'
        poster = video.with_suffix('.jpg')
        assert not video.exists() and not poster.exists(), 'Preserve an existing revision'
        run(['ffmpeg', '-y', '-v', 'error', '-i', original, '-filter_complex', wheel_support_filter(),
             '-map', '[clean]', '-map', '0:a:0', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
             '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
             '-c:a', 'copy', '-map_metadata', '0', '-metadata', f'title={TITLE}', '-movflags', '+faststart', video])
        run(['ffmpeg', '-y', '-v', 'error', '-ss', '6', '-i', video, '-frames:v', '1', '-q:v', '2', poster])
        item['video'] = dict(path=str(video.relative_to(ROOT)), sha256=sha(video))
        item['poster'] = dict(path=str(poster.relative_to(ROOT)), sha256=sha(poster))
        print(f'Removed bicycle supports: {locale}', flush=True)
    publish()
    raise SystemExit(0)

if args.retitle_only:
    assert previous.get('version') == VERSION, 'Retitle only the completed current version'
    assert set(args.locales) == set(COPY), 'Shared title metadata must update all locales together'
    for tag, fields in previous.get('renderedCopy', {}).items():
        assert all(COPY[tag][key] == value for key, value in fields.items()), 'Movie copy changed; render the film'
    for path, expected in previous['sources'].items():
        if path not in [str(Path(__file__).relative_to(ROOT)), 'src/i18n/yilo-hero-copy.json']:
            assert sha(ROOT / path) == expected, f'Movie source changed; render the film: {path}'
    for locale in args.locales:
        item = outputs[locale]
        video = ROOT / item['video']['path']
        temporary = CACHE / f'{locale}-metadata.mp4'
        run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-map', '0', '-c', 'copy',
             '-map_metadata', '0', '-metadata', f'title={TITLE}', '-movflags', '+faststart', temporary])
        temporary.replace(video)
        item['video']['sha256'] = sha(video)
    publish()
    print('Updated movie titles without re-encoding picture or sound.', flush=True)
    raise SystemExit(0)

for locale in args.locales:
    props = CACHE / f'{locale}.json'
    props.write_text(json.dumps({'locale': locale}))
    raw = CACHE / f'{locale}-silent.mp4'
    published_video = PUBLIC / f'hero-{locale}-{VERSION}.mp4'
    published_poster = published_video.with_suffix('.jpg')
    video = CACHE / f'{locale}-final.mp4'
    poster = CACHE / f'{locale}-final.jpg'
    run(['pnpm', 'exec', 'remotion', 'render', 'src/index.ts', 'YiloLineHero', raw,
         '--props', props, '--codec', 'h264', '--crf', '18', '--pixel-format', 'yuv420p',
         '--concurrency', '4', '--port', str(3400+list(COPY).index(locale)), '--browser-executable', BROWSER])
    credits = (ROOT / 'scripts/assets/yilo/hero-music-credits.txt').read_text()
    run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-i', PROJECT / 'public/music.wav',
         '-filter_complex', '[0:v]scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p[graded];'+wheel_support_filter('graded'),
         '-map', '[clean]', '-map', '1:a:0', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-color_range', 'tv',
         '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-c:a', 'aac', '-b:a', '192k',
         '-ar', '48000', '-ac', '2', '-t', '14', '-movflags', '+faststart', '-metadata', f'title={TITLE}',
         '-metadata', f'comment={COMMENT}', '-metadata', f'copyright={credits}', video])
    run(['ffmpeg', '-y', '-v', 'error', '-ss', '6', '-i', video, '-frames:v', '1', '-q:v', '2', poster])
    probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True))
    v = next(stream for stream in probe['streams'] if stream['codec_type']=='video')
    a = next(stream for stream in probe['streams'] if stream['codec_type']=='audio')
    assert [v['width'],v['height'],v['codec_name'],v['pix_fmt'],int(v['nb_frames'])] == [1280,608,'h264','yuv420p',336]
    if published_video.exists() or published_poster.exists():
        archive = CACHE / 'revisions' / datetime.now().strftime('%Y%m%d-%H%M%S')
        archive.mkdir(parents=True, exist_ok=True)
        for path in (published_video, published_poster):
            if path.exists(): shutil.copy2(path, archive / path.name)
    video.replace(published_video)
    poster.replace(published_poster)
    video, poster = published_video, published_poster
    outputs[locale] = dict(locale=locale,width=1280,height=608,fps=24,frames=336,seconds=14,codec='h264',pixelFormat='yuv420p',
        audio=dict(codec=a['codec_name'],sampleRate=a['sample_rate'],channels=a['channels']),
        video=dict(path=str(video.relative_to(ROOT)),sha256=sha(video)),poster=dict(path=str(poster.relative_to(ROOT)),sha256=sha(poster)))
    raw.unlink()
    publish()
    print(f'Exported {locale}: {video.stat().st_size:,} bytes',flush=True)
