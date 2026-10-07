"""Open an isolated Chrome recording window with audible autoplay enabled."""
import argparse
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:4330/world-book/')
    parser.add_argument('--chrome', type=Path, default=Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'))
    args = parser.parse_args()
    if not args.chrome.is_file():
        parser.error('Chrome was not found. Specify its executable with --chrome.')
    target = urlsplit(args.url)
    if target.scheme not in ('http', 'https') or target.hostname not in ('localhost', '127.0.0.1', '::1'):
        parser.error('--url must point to a local Astro dev server (localhost, 127.0.0.1 or ::1).')
    query = dict(parse_qsl(target.query))
    query['record'] = '1'
    url = urlunsplit(target._replace(query=urlencode(query)))
    with tempfile.TemporaryDirectory(prefix='world-book-recording-') as profile:
        print(f'Recording window: {url}', flush=True)
        print('Audible autoplay enabled for this temporary Chrome session. Close the window after recording.', flush=True)
        subprocess.run([
            str(args.chrome), f'--user-data-dir={profile}',
            '--no-first-run', '--no-default-browser-check',
            '--autoplay-policy=no-user-gesture-required',
            '--window-size=1440,1000', f'--app={url}',
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


if __name__ == '__main__':
    main()
