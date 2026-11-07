#!/usr/bin/env python3
"""Capture localized native Yilo views using samples in the matching source language."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import plistlib
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TAGS = json.loads((ROOT / "src/content/presskit-supported-languages.json").read_text())["yilo"]["tags"]
NAMES = ("learning-record.png", "learning-settings.png", "language-selection.png")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--app-source", type=Path, required=True)
parser.add_argument("--locales", nargs="+", choices=TAGS, default=TAGS)
args = parser.parse_args()
app = args.app_source.resolve()
output = ROOT / "scripts/assets/presskit/yilo"
fixture = ROOT / "scripts/assets/yilo/capture/YiloWebsiteCapture.swift"
commit = subprocess.check_output(["git", "-C", str(app), "rev-parse", "HEAD"], text=True).strip()
receipt_path = ROOT / "scripts/assets/presskit/screenshot-sources.json"
receipts = json.loads(receipt_path.read_text())
captures = [capture for capture in receipts["yilo"]["captures"] if capture["contentLanguage"] not in args.locales or Path(capture["source"]).name not in NAMES]
today = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()

with tempfile.TemporaryDirectory(prefix="yilo-website-capture-") as temporary:
    package = Path(temporary)
    for filename in ("Package.swift", "Package.resolved"):
        shutil.copy2(app / filename, package / filename)
    manifest = package / "Package.swift"
    content = manifest.read_text()
    content = content.replace('        .executableTarget(\n            name: "YiYanApp",', '        .executableTarget(name: "YiloWebsiteCapture", dependencies: ["YiYanUI", "YiYanCore"]),\n        .executableTarget(\n            name: "YiYanApp",')
    manifest.write_text(content)
    shutil.copytree(app / "Sources", package / "Sources")
    shutil.copytree(app / "Tests", package / "Tests")
    capture_source = package / "Sources/YiloWebsiteCapture"
    capture_source.mkdir()
    shutil.copy2(fixture, capture_source / fixture.name)
    env = {**os.environ, "DEVELOPER_DIR": "/Applications/Xcode.app/Contents/Developer"}
    build = ["swift", "build", "--package-path", str(package), "--scratch-path", str(ROOT / ".build/yilo-native-capture-swift")]
    subprocess.run(build + ["--product", "YiloWebsiteCapture"], env=env, check=True)
    products = Path(subprocess.check_output(build + ["--show-bin-path"], env=env, text=True).strip())
    capture_app = package / "Yilo Website Capture.app/Contents"
    (capture_app / "MacOS").mkdir(parents=True)
    (capture_app / "Resources").mkdir()
    shutil.copy2(products / "YiloWebsiteCapture", capture_app / "MacOS/YiloWebsiteCapture")
    for bundle in products.glob("*.bundle"):
        shutil.copytree(bundle, capture_app / "Resources" / bundle.name)
    for resource in (package / "Sources/YiYanUI/Resources").glob("*.lproj"):
        shutil.copytree(resource, capture_app / "Resources" / resource.name)
    (capture_app / "Info.plist").write_bytes(plistlib.dumps({
        "CFBundleExecutable": "YiloWebsiteCapture", "CFBundleIdentifier": "com.lazyapps.yilo.website-capture",
        "CFBundlePackageType": "APPL", "CFBundleDevelopmentRegion": "en",
        "CFBundleLocalizations": ["en", "zh-Hans", "zh-Hant", "es", "pt-BR", "fr", "de", "ja", "ko", "ru", "ar", "hi"]
    }))
    for tag in args.locales:
        folder = output / tag
        folder.mkdir(parents=True, exist_ok=True)
        record = fixture.parent / "records" / f"{tag}.json"
        sample = json.loads(record.read_text())
        assert sample["configuration"]["sourceLanguage"] == tag
        assert tag not in sample["configuration"]["targetLanguages"]
        capture_env = {**env, "YILO_CAPTURE_DIR": str(folder), "YILO_CAPTURE_LOCALE": tag, "YILO_CAPTURE_RECORD": str(record), "TZ": "Asia/Shanghai"}
        subprocess.run([str(capture_app / "MacOS/YiloWebsiteCapture"), "-AppleLanguages", f"({tag})", "-AppleLocale", tag], env=capture_env, check=True)
        native = json.loads((folder / "locale.json").read_text())
        assert native["nativeLocale"] == tag, f"Native locale mismatch: {tag}"
        source_files = ["Sources/YiYanUI/Views/RecordCardView.swift", "Sources/YiYanUI/Views/TargetTranslationSection.swift", "Sources/YiYanUI/Views/LearningLanguageSettingsView.swift", "Sources/YiYanUI/ViewModels/AppLocalization.swift", "Sources/YiYanCore/Presentation/ChineseReading.swift"]
        source_files += [str(path.relative_to(package)) for pattern in ("*Japanese*.swift", "TargetTranslationText.swift") for path in (package / "Sources").rglob(pattern)]
        for name in NAMES:
            captures.append({
                "source": str((folder / name).relative_to(ROOT)), "sha256": sha(folder / name),
                "contentLanguage": tag, "type": "native", "capturedOn": today, "appSourceCommit": commit,
                "originalSource": str(fixture.relative_to(ROOT)),
                "operation": "Unmodified native AppKit/SwiftUI component export using the app's own localization resources. Sample input, source setting and learning explanations match the UI language. English learns Simplified Chinese/Japanese; Japanese learns English/Simplified Chinese; other locales learn English/Japanese. Settings use isolated sample preferences. No image text replacement, resizing or UI reconstruction. Not a full app window.",
                "appearance": "dark" if name == "learning-record.png" else "light",
                "captureFixtureSha256": sha(fixture), "nativeLocale": native["nativeLocale"], "nativeLabels": native["labels"],
                "sourceLanguage": native["sourceLanguage"], "targetLanguages": native["targetLanguages"],
                "localizationSha256": sha(package / f"Sources/YiYanUI/Resources/{tag}.lproj/Localizable.strings"),
                "sourceFiles": {file: sha(package / file) for file in sorted(source_files)},
                **({"recordSource": str(record.relative_to(ROOT)), "recordSha256": sha(record)} if name == "learning-record.png" else {})
            })
        print("Native captures exported:", tag, flush=True)

receipts["yilo"] = {"checkedOn": today, "appSourceCommit": commit,
    "sourceState": "Localized native components from a source snapshot. Every example input, source setting and explanation matches its UI locale. English learns Simplified Chinese/Japanese; Japanese learns English/Simplified Chinese; other locales learn English/Japanese. Settings use disposable sample preferences.",
    "captures": sorted(captures, key=lambda capture: capture["source"])}
receipt_path.write_text(json.dumps(receipts, ensure_ascii=False, indent=2) + "\n")
