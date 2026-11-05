"""Validate local GitHub profile SVG assets and README references."""
import pathlib
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "profile-v2"
README = (ROOT / "README.md").read_text(encoding="utf-8")
EXPECTED = {
    "hero-dark.svg", "hero-light.svg", "strata-dark.svg", "strata-light.svg",
    "contrib-3d-dark.svg", "contrib-3d-light.svg", "snake-dark.svg", "snake-light.svg",
}
files = list(ASSETS.glob("*.svg"))
assert {path.name for path in files} == EXPECTED, "Missing/extra SVG assets"
for path in files:
    root = ET.parse(path).getroot()
    assert root.tag == "{http://www.w3.org/2000/svg}svg", path

pattern = r"https://raw\\.githubusercontent\\.com/hienpham0344/hienpham0344/([a-f0-9]{40})/(assets/profile-v2/[\\w-]+\\.svg)"
matches = re.findall(pattern, README)
assert matches, "No pinned SVG references"
shas = {sha for sha, _ in matches}
assert len(shas) == 1, "Artwork must use a single immutable commit"
referenced = {pathlib.PurePosixPath(path).name for _, path in matches}
assert referenced == EXPECTED, f"Artwork reference mismatch: {EXPECTED ^ referenced}"
for sha, path in set(matches):
    subprocess.run(["git", "cat-file", "-e", f"{sha}:{path}"], cwd=ROOT, check=True)
assert "</td>" not in README and "<table" not in README, "Unsafe raw HTML tables"
assert "github-readme-stats" not in README, "Third-party stats image disallowed"
print("OK: all 8 SVGs parse and README references exist in immutable Git commit.")
