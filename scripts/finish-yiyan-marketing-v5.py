"""Add a credited CC BY 4.0 piano excerpt to the local H3 agent comedy.

Download the original from the verified author's URL in music-credits.txt into
scripts/assets/yiyan/marketing-v4/music/AKindOfHope.mp3 before running.
"""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/yiyan/marketing-v5'
PUBLIC = ROOT / 'public/v/yiyan'
REVIEW = ROOT / 'docs/reviews/yiyan-agents-20261008'
COPY = json.loads((ROOT / 'src/i18n/yiyan-agent-film-copy.json').read_text())
TRACK = ROOT / 'scripts/assets/yiyan/marketing-v4/music/AKindOfHope.mp3'
CREDIT = ('A Kind Of Hope by Scott Buckley — CC BY 4.0. '
          'https://www.scottbuckley.com.au/library/a-kind-of-hope/ '
          'https://creativecommons.org/licenses/by/4.0/ '
          'Edited: 14-second excerpt, volume adjusted, fades applied.')


def run(args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True, text=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-count_frames', '-show_format', '-show_streams', '-of', 'json', path]).stdout)


if __name__ == '__main__':
    (ASSETS / 'music').mkdir(exist_ok=True)
    silent = ASSETS / 'silent'
    silent.mkdir(exist_ok=True)
    soundtrack = ASSETS / 'music/soundtrack.wav'
    if not soundtrack.exists():
        # A quiet opening piano phrase, no percussion or vocal. Preserve its dynamics.
        run(['ffmpeg', '-v', 'error', '-ss', '6', '-i', TRACK, '-t', '14', '-af',
             'loudnorm=I=-24:TP=-3:LRA=11,afade=t=in:st=0:d=0.5,afade=t=out:st=12.6:d=1.4',
             '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s24le', soundtrack])
    records = []
    for locale in COPY:
        output = PUBLIC / f'hero-{locale}-v5.mp4'
        base = silent / output.name
        assert base.exists(), f'Run the v5 composer first: {base}'
        if output.exists():
            raise RuntimeError(f'Preserve existing final export: {output}')
        run(['ffmpeg', '-v', 'error', '-i', base, '-i', soundtrack, '-map', '0:v:0', '-map', '1:a:0',
             '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', '14', '-movflags', '+faststart',
             '-metadata', f'comment=AI-animated fictional parody; local MiniMax H3 character animation. Editorial language examples; no actual Trump footage, voice or endorsement. {CREDIT}',
             '-metadata', f'copyright=Music: {CREDIT}', output])
        p = probe(output)
        video = next(s for s in p['streams'] if s['codec_type'] == 'video')
        audio = next(s for s in p['streams'] if s['codec_type'] == 'audio')
        assert (video['width'], video['height'], video['nb_read_frames']) == (1280, 720, '336')
        assert video['codec_name'] == 'h264' and video['pix_fmt'] == 'yuv420p'
        assert audio['codec_name'] == 'aac' and audio['sample_rate'] == '48000' and audio['channels'] == 2
        assert abs(float(p['format']['duration']) - 14) < 0.05
        # Stream copy must retain every encoded video packet exactly.
        hashes = [run(['ffmpeg', '-v', 'error', '-i', f, '-map', '0:v:0', '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-']).stdout.strip() for f in [base, output]]
        assert hashes[0] == hashes[1]
        records.append(dict(locale=locale, path=str(output.relative_to(ROOT)), bytes=output.stat().st_size,
                            sha256=sha(output), silent_sha256=sha(base), video_packet_hash=hashes[0], probe=p))
        print(output, flush=True)
    loudness = run(['ffmpeg', '-hide_banner', '-i', PUBLIC / 'hero-zh-hans-v5.mp4', '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
    summary = '\n'.join(line.rstrip() for line in loudness[loudness.rfind('Summary:'):].splitlines())
    (REVIEW / 'audio-loudness.txt').write_text(summary + '\n')
    (REVIEW / 'validation.json').write_text(json.dumps(dict(
        music=dict(title='A Kind Of Hope', creator='Scott Buckley', license='CC BY 4.0',
                   source='https://www.scottbuckley.com.au/library/a-kind-of-hope/',
                   download='https://www.scottbuckley.com.au/library/wp-content/uploads/2022/10/AKindOfHope.mp3',
                   license_url='https://creativecommons.org/licenses/by/4.0/', checked='2026-10-08',
                   track_sha256=sha(TRACK), soundtrack_sha256=sha(soundtrack), excerpt_seconds=[6,20],
                   processing='loudnorm -24 LUFS, fade in 0.5s, fade out 1.4s; AAC 192 kbps'),
        current_icon_sha256=sha(ROOT / 'src/assets/img/yiyan-icon.png'),
        outputs=records), ensure_ascii=False, indent=2) + '\n')
