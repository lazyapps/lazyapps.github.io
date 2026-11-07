#!/usr/bin/env python3
"""Capture localized native Yilo views using a short sample and the native extra-large text setting."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import plistlib
import struct
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TAGS = json.loads((ROOT / "src/content/presskit-supported-languages.json").read_text())["yilo"]["tags"]
NAMES = ("hero-record.png",)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--app-source", type=Path, required=True)
parser.add_argument("--locales", nargs="+", choices=TAGS, default=TAGS)
args = parser.parse_args()
app = args.app_source.resolve()
output = ROOT / "scripts/assets/presskit/yilo"
fixture = ROOT / "scripts/assets/yilo/capture/YiloHeroCapture.swift"
commit = subprocess.check_output(["git", "-C", str(app), "rev-parse", "HEAD"], text=True).strip()
receipt_path = ROOT / "scripts/assets/presskit/screenshot-sources.json"
receipts = json.loads(receipt_path.read_text())
captures = [capture for capture in receipts["yilo"]["captures"] if capture["contentLanguage"] not in args.locales or not capture["source"].endswith("/hero-record.png")]
today = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()

with tempfile.TemporaryDirectory(prefix="yilo-hero-capture-") as temporary:
    package = Path(temporary)
    for filename in ("Package.swift", "Package.resolved"):
        shutil.copy2(app / filename, package / filename)
    manifest = package / "Package.swift"
    content = manifest.read_text()
    content = content.replace('        .executableTarget(\n            name: "YiYanApp",', '        .executableTarget(name: "YiloHeroCapture", dependencies: ["YiYanUI", "YiYanCore"]),\n        .executableTarget(\n            name: "YiYanApp",')
    manifest.write_text(content)
    shutil.copytree(app / "Sources", package / "Sources")
    shutil.copytree(app / "Tests", package / "Tests")
    capture_source = package / "Sources/YiloHeroCapture"
    capture_source.mkdir()
    shutil.copy2(fixture, capture_source / fixture.name)
    env = {**os.environ, "DEVELOPER_DIR": "/Applications/Xcode.app/Contents/Developer"}
    build = ["swift", "build", "--package-path", str(package), "--scratch-path", str(ROOT / ".build/yilo-native-capture-swift")]
    subprocess.run(build + ["--product", "YiloHeroCapture"], env=env, check=True)
    products = Path(subprocess.check_output(build + ["--show-bin-path"], env=env, text=True).strip())
    capture_app = package / "Yilo Hero Capture.app/Contents"
    (capture_app / "MacOS").mkdir(parents=True)
    (capture_app / "Resources").mkdir()
    shutil.copy2(products / "YiloHeroCapture", capture_app / "MacOS/YiloHeroCapture")
    for bundle in products.glob("*.bundle"):
        shutil.copytree(bundle, capture_app / "Resources" / bundle.name)
    for resource in (package / "Sources/YiYanUI/Resources").glob("*.lproj"):
        shutil.copytree(resource, capture_app / "Resources" / resource.name)
    (capture_app / "Info.plist").write_bytes(plistlib.dumps({
        "CFBundleExecutable": "YiloHeroCapture", "CFBundleIdentifier": "com.lazyapps.yilo.hero-capture",
        "CFBundlePackageType": "APPL", "CFBundleDevelopmentRegion": "en",
        "CFBundleLocalizations": ["en", "zh-Hans", "zh-Hant", "es", "pt-BR", "fr", "de", "ja", "ko", "ru", "ar", "hi"]
    }))
    for tag in args.locales:
        folder = output / tag
        folder.mkdir(parents=True, exist_ok=True)
        record = fixture.parent / "hero-records" / f"{tag}.json"
        sample = json.loads(record.read_text())
        assert sample["configuration"]["sourceLanguage"] == tag
        assert tag not in sample["configuration"]["targetLanguages"]
        capture_env = {**env, "YILO_CAPTURE_DIR": str(folder), "YILO_CAPTURE_LOCALE": tag, "YILO_CAPTURE_RECORD": str(record), "TZ": "Asia/Shanghai"}
        subprocess.run([str(capture_app / "MacOS/YiloHeroCapture"), "-AppleLanguages", f"({tag})", "-AppleLocale", tag], env=capture_env, check=True)
        native = json.loads((folder / "hero-locale.json").read_text())
        assert native["nativeLocale"] == tag, f"Native locale mismatch: {tag}"
        source_files = ["Sources/YiYanUI/Views/RecordCardView.swift", "Sources/YiYanUI/Views/TargetTranslationSection.swift", "Sources/YiYanUI/Views/LearningLanguageSettingsView.swift", "Sources/YiYanUI/ViewModels/AppLocalization.swift", "Sources/YiYanUI/Views/MainWindowTypography.swift", "Sources/YiYanCore/Presentation/ChineseReading.swift"]
        source_files += [str(path.relative_to(package)) for pattern in ("*Japanese*.swift", "TargetTranslationText.swift") for path in (package / "Sources").rglob(pattern)]
        for name in NAMES:
            captures.append({
                "source": str((folder / name).relative_to(ROOT)), "sha256": sha(folder / name),
                "contentLanguage": tag, "type": "native", "capturedOn": today, "appSourceCommit": commit,
                "originalSource": str(fixture.relative_to(ROOT)),
                "operation": "Unmodified native RecordCardView export with a short isolated sample record, the app's extraLarge text preference, native Pinyin/Romaji and collapsed learning notes. No image text replacement, resizing or UI reconstruction. Not a full app window.",
                "appearance": "light",
                "captureFixtureSha256": sha(fixture), "nativeLocale": native["nativeLocale"], "nativeLabels": native["labels"],
                "sourceLanguage": native["sourceLanguage"], "targetLanguages": native["targetLanguages"],
                "localizationSha256": sha(package / f"Sources/YiYanUI/Resources/{tag}.lproj/Localizable.strings"),
                "sourceFiles": {file: sha(package / file) for file in sorted(source_files)},
                **({"recordSource": str(record.relative_to(ROOT)), "recordSha256": sha(record)} if name == "hero-record.png" else {})
            })
        print("Native captures exported:", tag, flush=True)

receipts["yilo"] = {"checkedOn": today, "appSourceCommit": commit,
    "sourceState": "Localized native component exports from isolated source snapshots. Every product and hero example uses input and source settings matching its UI locale. Short hero samples use the native extraLarge text preference. Settings use disposable sample preferences.",
    "captures": sorted(captures, key=lambda capture: capture["source"])}
receipt_path.write_text(json.dumps(receipts, ensure_ascii=False, indent=2) + "\n")

hero_captures = [capture for capture in receipts["yilo"]["captures"] if capture["source"].endswith("/hero-record.png")]
for capture in hero_captures:
    capture["nativeTextSize"] = "extraLarge"
    capture["nativeFrameWidthPoints"] = 520
    capture["pixelWidth"], capture["pixelHeight"] = struct.unpack(">II", (ROOT / capture["source"]).read_bytes()[16:24])
receipt_path.write_text(json.dumps(receipts, ensure_ascii=False, indent=2) + "\n")
(ROOT / "scripts/assets/yilo/hero-native-source.json").write_text(json.dumps({"checkedOn": today, "appSourceCommit": commit, "captures": hero_captures}, ensure_ascii=False, indent=2) + "\n")
records = ROOT / "video/yilo-hero/public/records"
records.mkdir(parents=True, exist_ok=True)
for capture in hero_captures:
    shutil.copyfile(ROOT / capture["source"], records / (capture["contentLanguage"].lower() + ".png"))
