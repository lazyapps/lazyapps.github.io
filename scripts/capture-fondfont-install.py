"""Capture current, localized FondFont UI through Argent; never install a profile.

Only the disposable FondFont Site Capture simulator below is modified. Original
debug simulators and the iOS repository are untouched. Screenshots stay intact.
"""
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
IOS = Path('/Users/realazy/Projects/iOS/iOSFontInstaller')
OUT = ROOT / 'scripts/assets/fondfont/install-capture-20261007'
UDID = '7EA1579B-3ED0-44E6-8048-1711D6151161'
APP = 'com.lazyapps.iOSFontInstaller'
DEVICE = Path.home() / 'Library/Developer/CoreSimulator/Devices' / UDID
V8 = ROOT / 'scripts/assets/fondfont/animation/v8/fonts'
V9 = ROOT / 'scripts/assets/fondfont/animation/v9/fonts'
STORE_FONTS = IOS / 'AppStore/Screenshots/public/fonts'
FIXTURES = IOS / 'AppStore/Captures/Fixtures'
LOCALES = {
    'en': ('en', 'en_US', 'Edit', 'Allow', ['Allura', 'Bebas Neue', 'DINish']),
    'zh-hans': ('zh-Hans', 'zh_CN', '编辑', '允许', ['Ma Shan Zheng', 'WDXL', 'ZCOOL']),
    'zh-hant': ('zh-Hant', 'zh_TW', '編輯', '允許', ['Huninn|粉圓', 'Iansui|芫荽', 'LXGW|霞[鹜鶩]']),
    'ja': ('ja', 'ja_JP', '編集', '許可', ['Kosugi Maru', 'M PLUS|Rounded Mplus', 'Zen Maru Gothic']),
    'ko': ('ko', 'ko_KR', '편집', '허용', ['Dongle', 'Jua', 'Sunflower']),
    'fr': ('fr', 'fr_FR', 'Modifier', 'Autoriser', ['Allura', 'Bebas Neue', 'DINish']),
    'de': ('de', 'de_DE', 'Bearbeiten', 'Zulassen', ['Allura', 'Bebas Neue', 'DINish']),
}
FRAME = re.compile(r'^\s*(AX\w+)\s+"([^"]*)"(.*?)\s+\(([\d.]+), ([\d.]+), ([\d.]+), ([\d.]+)\)$')


def command(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=120, **kwargs).stdout


def tool(name, **args):
    raw = command(['argent', 'run', name, '--args', json.dumps({'udid': UDID, **args}), '--json'])
    result = json.loads(raw)
    if result.get('error'):
        raise RuntimeError(result)
    return result


def read():
    text = tool('describe')['description']
    elements = []
    for line in text.splitlines():
        m = FRAME.match(line)
        if m:
            role, label, attrs = m.group(1, 2, 3)
            x, y, w, h = map(float, m.group(4, 5, 6, 7))
            if w > .01 and h > .008:
                elements.append(dict(role=role, label=label, attrs=attrs, x=x, y=y, w=w, h=h))
    return text, elements


def wait_find(pattern, *, role='AXButton', attrs=False, min_y=0, max_y=1, timeout=20):
    start = time.monotonic()
    while True:
        text, elements = read()
        matches = [e for e in elements if e['role'] == role and min_y <= e['y'] < max_y
                   and re.search(pattern, e['attrs'] if attrs else e['label'])]
        if matches:
            return matches[0]
        if time.monotonic() - start > timeout:
            raise RuntimeError(f'Cannot find {pattern}:\n{text}')
        time.sleep(.3)


def tap(e):
    y=e['y']+e['h']/2
    if e['w']>.5 and re.search(r'\.(ttf|otf|ttc)',e['label']):
        y=min(y,.905)  # Last row can extend behind the floating bottom toolbar.
    tool('gesture-tap', x=e['x']+e['w']/2, y=y)
    time.sleep(.55)


def screenshot(folder, name):
    tool('await-screen-idle', timeoutMs=4000, minStableMs=500)
    target = folder / f'{name}.png'
    command(['argent', 'run', 'screenshot', '--udid', UDID, '--scale', '1', '--out', str(target)])
    _, elements = read()
    (folder / f'{name}.ax.json').write_text(json.dumps(elements, ensure_ascii=False, indent=2)+'\n')
    return {'file': target.name, 'bytes': target.stat().st_size,
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}


def font_set(code):
    common = [
        (V9/'Allura-Regular.ttf', V9/'allura-OFL.txt'),
        (FIXTURES/'latin-fonts/BebasNeue-Regular.ttf', FIXTURES/'latin-fonts/OFL.txt'),
        (V8/'DINish-Regular.otf', V8/'DINish-OFL.txt'),
        (STORE_FONTS/'IBMPlexMono-Regular.ttf', STORE_FONTS/'licenses/IBMPlexMono-OFL.txt'),
        (STORE_FONTS/'PlayfairDisplay-Variable.ttf', STORE_FONTS/'licenses/PlayfairDisplay-OFL.txt'),
    ]
    app_locale = LOCALES[code][0]
    if code in ('en', 'fr', 'de'):
        return common + [
            (STORE_FONTS/'Inter-Variable.ttf', STORE_FONTS/'licenses/Inter-OFL.txt'),
            (STORE_FONTS/'InterTight-Variable.ttf', STORE_FONTS/'licenses/InterTight-OFL.txt'),
            (V8/'EBGaramond[wght].ttf', V8/'EBGaramond-OFL.txt'),
            (V8/'LibreBaskerville[wght].ttf', V8/'LibreBaskerville-OFL.txt'),
        ]
    manifest_path = FIXTURES / 'cjk-fonts' / app_locale / 'manifest.json'
    data = json.loads(manifest_path.read_text())
    regional = [(manifest_path.parent/f['file'], manifest_path.parent/f['licenseFile']) for f in data['fonts']]
    serif = {'zh-hans':'SourceHanSerifSC-Regular.otf', 'zh-hant':'SourceHanSerifTC-Regular.otf',
             'ja':'SourceHanSerif-Regular.otf', 'ko':'SourceHanSerifK-Regular.otf'}[code]
    return common + regional + [(V8/serif, V8/'SourceHanSerif-LICENSE.txt')]


def font_record(font, license):
    assert font.is_file() and license.is_file(), (font, license)
    license_text=license.read_text(errors='replace')
    if 'OPEN FONT LICENSE' in license_text.upper() or 'license: "OFL"' in license_text:
        kind='SIL OFL 1.1'
        suffix='OFL' if license.suffix!='.pb' else 'license-metadata'
    elif 'Apache License' in license_text and 'Version 2.0' in license_text:
        kind='Apache 2.0'
        suffix='Apache-2.0'
    else:
        raise AssertionError(('Unknown font license',license))
    target=OUT/'licenses'/(font.stem+'-'+suffix+license.suffix)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(license,target)
    return {'file':font.name,'source':str(font),'license':kind,
            'licenseFile':str(target.relative_to(ROOT)),
            'sha256':hashlib.sha256(font.read_bytes()).hexdigest()}


def prepare(code):
    app_locale, region, *_ = LOCALES[code]
    # Offline simulator preferences are capture setup, not image alteration.
    subprocess.run(['xcrun', 'simctl', 'shutdown', UDID], capture_output=True)
    preferences = DEVICE / 'data/Library/Preferences/.GlobalPreferences.plist'
    data = plistlib.loads(preferences.read_bytes())
    data.update(AppleLanguages=list(dict.fromkeys([app_locale, 'en'])), AppleLocale=region, AppleICUForce24HourTime=False)
    preferences.write_bytes(plistlib.dumps(data, fmt=plistlib.FMT_BINARY))
    tool('boot-device', headless=True)
    command(['xcrun','simctl','status_bar',UDID,'override','--time','9:41','--dataNetwork','wifi',
             '--wifiMode','active','--wifiBars','3','--cellularMode','active','--cellularBars','4',
             '--batteryState','discharging','--batteryLevel','100'])
    container = Path(command(['xcrun','simctl','get_app_container',UDID,APP,'data']).strip())
    documents = container/'Documents'
    # This simulator was created only for this task; these are our own fixtures.
    for old in documents.iterdir():
        if old.suffix.lower() in ('.ttf','.otf','.ttc'):
            old.unlink()
    records=[]
    for font, license in font_set(code):
        record=font_record(font,license)
        shutil.copyfile(font,documents/font.name)
        records.append(record)
    tool('restart-app',bundleId=APP)
    return records


def capture(code, reuse=False):
    folder=OUT/code
    folder.mkdir(parents=True,exist_ok=True)
    app_locale, region, edit, allow, families=LOCALES[code]
    print(f'{code}: prepare current app and 9 open-source font families',flush=True)
    if reuse:
        tool('restart-app',bundleId=APP)
        fonts=[font_record(font,license) for font,license in font_set(code)]
    else:
        fonts=prepare(code)
    strings=dict(re.findall(r'^"(.*?)"\s*=\s*"(.*?)";', (IOS/f'iOSFontInstaller/{app_locale}.lproj/Localizable.strings').read_text(),re.M))
    tap(wait_find('^(?:'+re.escape(edit)+'|Edit)$'))
    remaining=list(families)
    for attempt in range(18):
        if not remaining:
            break
        _, elements=read()
        found=False
        for family in remaining:
            rows=[e for e in elements if e['role']=='AXButton' and e['w']>.5
                  and .17<e['y'] and e['y']+e['h']/2<.85 and re.search(f'(?:{family}).*[,、]',e['label'])]
            if rows:
                selected=f'value="{strings["Selected"]}"'
                if selected not in rows[0]['attrs']:
                    tap(rows[0])
                _, after=read()
                if any(re.search(f'(?:{family}).*[,、]',e['label']) and selected in e['attrs'] for e in after):
                    remaining.remove(family)
                    found=True
                break
        if not found:
            bars=[e for e in elements if e['role']=='AXGroup' and e['x']>.9 and e['h']>.5]
            assert bars, elements
            tool('gesture-swipe',fromX=bars[0]['x']-.3,fromY=.78,toX=bars[0]['x']-.3,toY=.31,durationMs=600,momentum=False)
    assert not remaining, 'Missing font families: '+str(remaining)
    install_label=strings.get('Install (%zd)','Install (%zd)').replace('%zd','3')
    install=wait_find('^'+re.escape(install_label)+'$')
    images=[screenshot(folder,'select')]
    tap(install)
    download=strings['FIInstallHTMLStartButton']
    download_button=wait_find('^'+re.escape(download)+'$')
    images.append(screenshot(folder,'guide'))
    tap(download_button)
    allow_button=wait_find('^'+re.escape(allow)+'$',min_y=.3)
    images.append(screenshot(folder,'permission'))
    tap(allow_button)
    close_label={'en':'Close','zh-hans':'关闭','zh-hant':'關閉','ja':'閉じる','ko':'닫기','fr':'Fermer','de':'Schließen'}[code]
    close=wait_find('^'+re.escape(close_label)+'$',min_y=.4,max_y=.75)
    # A system confirmation has one lower Close button. Require its group too.
    _, confirmation=read()
    assert any('Profile Downloaded' in e['label'] or e['role']=='AXGroup' and e['w']>.6 and .3<e['y']<.6 for e in confirmation)
    images.append(screenshot(folder,'downloaded'))
    tap(close)
    open_settings=wait_find('^'+re.escape(strings['FIInstallHTMLOpenSettingsButton'])+'$')
    tap(open_settings)
    downloaded=wait_find('com.apple.managedconfiguration.ios-purgatory',attrs=True,timeout=60)
    tap(downloaded)
    # Capture the review screen; do not tap its final Install button.
    install_system={'en':'Install','zh-hans':'安装','zh-hant':'安裝','ja':'インストール','ko':'설치','fr':'Installer','de':'Installieren'}[code]
    wait_find('^'+re.escape(install_system)+'$',min_y=.08,max_y=.14)
    time.sleep(.5)
    images.append(screenshot(folder,'profile'))
    save_manifest(code,fonts,images)


def save_manifest(code,fonts,images):
    app_locale,region,*_=LOCALES[code]
    folder=OUT/code
    manifest={'locale':code,'appLocale':app_locale,'region':region,'simulator':UDID,'device':'iPhone 17',
              'runtime':'iOS 27.0','sourceCommit':command(['git','-C',str(IOS),'rev-parse','HEAD']).strip(),
              'version':'260923.0','build':'Current source built on 2026-10-07; no app code modified.',
              'statusBar':{'time':'9:41','battery':100,'charging':False,'wifiBars':3,'cellularBars':4},
              'processing':'Full-resolution, unchanged Argent PNG captures. No retouch, crop or generated UI.',
              'profileInstalled':False,'fonts':fonts,'images':images}
    (folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(f'{code}: captured {len(images)} intact screens; {len(fonts)} open-source font families',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--reuse',action='store_true',help='Reuse the already prepared first locale after a failed capture.')
    parser.add_argument('locales',nargs='+',choices=LOCALES)
    args=parser.parse_args()
    for i,code in enumerate(args.locales):
        capture(code,reuse=args.reuse and i==0)
