from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path


CSS_IMAGE_RE = re.compile(r"'([^']+\.png)'")


def main() -> None:
    package = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("outputs/kurimanjyu-chic.ktheme")
    if not package.exists():
        raise SystemExit(f"Missing package: {package}")

    with zipfile.ZipFile(package) as zf:
        names = set(zf.namelist())
        css_name = "KakaoTalkTheme.css"
        if css_name not in names:
            raise SystemExit("KakaoTalkTheme.css must be at the archive root.")
        if any(name.startswith("__MACOSX/") or name.endswith(".DS_Store") for name in names):
            raise SystemExit("Archive contains macOS metadata.")
        if any(name.count("/") == 0 and name not in {css_name} for name in names):
            raise SystemExit("Unexpected root file found.")
        if any(name.startswith("kurimanjyu-ios-theme/") for name in names):
            raise SystemExit("Archive is wrapped in a folder; KakaoTalk expects root CSS + Images/.")

        css = zf.read(css_name).decode("utf-8")
        referenced = sorted(set(CSS_IMAGE_RE.findall(css)))
        missing = []
        for ref in referenced:
            candidates = [
                f"Images/{ref}",
                f"Images/{ref[:-4]}@2x.png",
                f"Images/{ref[:-4]}@3x.png",
            ]
            if not any(candidate in names for candidate in candidates):
                missing.append(ref)

    report = {
        "package": str(package.resolve()),
        "entry_count": len(names),
        "referenced_images": len(referenced),
        "missing_referenced_images": missing,
        "ok": not missing,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
