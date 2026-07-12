#!/usr/bin/env python3
"""Generate capabilities.json — a machine-readable index of what the SaasKiller
template provides, per optional feature.

It is generated from the SAME sources of truth setup.sh uses, so it can't drift
from reality:
  - setup.sh `strip_feature <name> <dirs...>`  → feature → apps/dirs it owns
  - `# === FEATURE: X === ... === END ===` markers in requirements.txt (pip deps)
  - the same markers in backend/.env.example (env vars a feature needs)
  - models.py in each feature's backend app  → Django models
  - urls.py include() lines                   → API endpoint prefixes

Run from the repo root:
    python3 scripts/gen_capabilities.py            # writes capabilities.json
    python3 scripts/gen_capabilities.py --check     # verify on-disk file is current (CI)

Nothing here is SaasKiller-name specific, so it keeps working in a fork after
setup.sh renames the project.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETUP = ROOT / "setup.sh"
REQS = ROOT / "backend" / "requirements.txt"
ENV_EXAMPLE = ROOT / "backend" / ".env.example"
OUT = ROOT / "capabilities.json"

# Human-readable one-liners per feature key (the only hand-maintained bit; keys
# are validated against setup.sh below so a typo/rename is caught).
DESCRIPTIONS = {
    "stripe": "Billing & payments via Stripe.",
    "workspaces": "Multi-tenant workspaces, memberships and invitations.",
    "cms": "feincms3 CMS — pages/blog, server-rendered Svelte islands, crawlable.",
    "tasks": "Background task queue and worker (django-q2).",
    "websockets": "Realtime via django-channels.",
    "s3": "File uploads to nine.ch S3 object storage.",
    "sentry": "Error monitoring via Sentry.",
    "apikeys": "Programmatic API key management.",
    "github-oauth": "GitHub OAuth as a second login provider.",
    "capacitor": "Capacitor mobile-app wrapper.",
    "i18n": "Paraglide multilingual UI (de/en).",
    "no-i18n": "",  # internal inverse marker, not a user feature — filtered out below
}

# Marker names that are not user-facing features (internal strip mechanics).
NON_FEATURES = {"no-i18n"}


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def feature_dirs_from_setup() -> dict[str, list[str]]:
    """Parse real `strip_feature` INVOCATIONS → {feature: [dirs]}.

    Only lines of the form `$USE_FOO || strip_feature <name> <dirs...>` count —
    this excludes the function definition and its explanatory comments, which
    also contain the word 'strip_feature'.
    """
    out: dict[str, list[str]] = {}
    for raw in read(SETUP).splitlines():
        line = raw.strip()
        if line.startswith("#"):
            continue                       # comment
        if "strip_feature()" in line:
            continue                       # the function definition
        # A real invocation: `strip_feature <name> [dirs...]`, possibly after
        # `$USE_X ||` or inside an if-branch. Require it to be a command, i.e.
        # `strip_feature` is either at start or right after `|| ` / `; ` / `then `.
        m = re.search(r"(?:^|\|\||;|then|else)\s*strip_feature\s+([a-z0-9-]+)\s*(.*)$",
                      line)
        if not m:
            continue
        name = m.group(1)
        rest = re.sub(r"#.*$", "", m.group(2)).strip()
        dirs = rest.split() if rest else []
        # Keep the union of dirs if a feature is stripped in more than one branch.
        out.setdefault(name, [])
        for d in dirs:
            if d not in out[name]:
                out[name].append(d)
    return out


def marker_blocks(text: str, feature: str) -> list[str]:
    """Return the inner text of every `=== FEATURE: X === ... === END ===` block."""
    pat = re.compile(
        r"===\s*FEATURE:\s*" + re.escape(feature) + r"\s*==={0,3}(.*?)"
        r"===\s*END FEATURE:\s*" + re.escape(feature) + r"\s*===",
        re.DOTALL,
    )
    return [m.group(1) for m in pat.finditer(text)]


def pip_deps(feature: str) -> list[str]:
    deps = []
    for block in marker_blocks(read(REQS), feature):
        for ln in block.splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                deps.append(ln)
    return deps


def env_vars(feature: str) -> list[str]:
    names = []
    for block in marker_blocks(read(ENV_EXAMPLE), feature):
        for ln in block.splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                names.append(ln.split("=", 1)[0].strip())
    return names


def models_in(app_dir: Path) -> list[str]:
    mp = app_dir / "models.py"
    if not mp.exists():
        return []
    src = read(mp)
    # class Foo(...models.Model / AbstractUser / MPTTModel ...)
    return re.findall(r"^class\s+([A-Za-z0-9_]+)\s*\(", src, re.MULTILINE)


def endpoints_for_dirs(dirs: list[str]) -> list[str]:
    """Find API path prefixes wired for a feature's backend apps.

    Looks in the root urls.py for include() lines that mention the app module.
    """
    urls_text = ""
    for cand in (ROOT / "backend").glob("*/urls.py"):
        # the project urls.py (has ROOT_URLCONF-style includes)
        t = read(cand)
        if "include(" in t and "api/" in t:
            urls_text += t + "\n"
    eps = []
    for d in dirs:
        app = Path(d).name  # e.g. backend/billing -> billing
        if not d.startswith("backend/"):
            continue
        # path("api/billing/", include("billing.urls"))
        for m in re.finditer(r'path\(\s*["\']([^"\']+)["\']\s*,\s*include\(\s*["\']'
                              + re.escape(app) + r'\.', urls_text):
            eps.append(m.group(1))
    return sorted(set(eps))


def fe_paths(dirs: list[str]) -> dict[str, list[str]]:
    """Split a feature's frontend paths into route dirs vs. other files/config."""
    routes, files = [], []
    for d in dirs:
        if not d.startswith("frontend/"):
            continue
        if d.startswith("frontend/src/routes/"):
            routes.append(d)
        else:
            files.append(d)
    return {"routes": sorted(routes), "files": sorted(files)}


def build() -> dict:
    feat_dirs = feature_dirs_from_setup()
    features = {}
    for feature, dirs in sorted(feat_dirs.items()):
        if feature in NON_FEATURES:
            continue
        # A real Django app dir has an apps.py or models.py (not e.g. static/islands).
        backend_apps = sorted({
            Path(d).name for d in dirs
            if d.startswith("backend/") and (ROOT / d).is_dir()
            and ((ROOT / d / "apps.py").exists() or (ROOT / d / "models.py").exists())
        })
        models = []
        for d in dirs:
            if d.startswith("backend/"):
                models += [f"{Path(d).name}.{m}" for m in models_in(ROOT / d)]
        fe = fe_paths(dirs)
        # "present" = at least one of its owned paths still exists on disk. In the
        # template all are present; in a fork, stripped features report present=false.
        present = any((ROOT / d).exists() for d in dirs) if dirs else \
            bool(pip_deps(feature) or env_vars(feature))
        features[feature] = {
            "description": DESCRIPTIONS.get(feature, ""),
            "present": present,
            "config_key": "mobile" if feature == "capacitor"
                          else ("github_oauth" if feature == "github-oauth" else feature),
            "backend_apps": backend_apps,
            "models": sorted(models),
            "api_endpoints": endpoints_for_dirs(dirs),
            "frontend_routes": fe["routes"],
            "frontend_files": fe["files"],
            "pip_dependencies": pip_deps(feature),
            "env_vars": env_vars(feature),
            "removed_paths_when_disabled": dirs,
        }
    return {
        "_generated_by": "scripts/gen_capabilities.py",
        "_note": "Machine-readable index of optional features. Regenerate with "
                 "`python3 scripts/gen_capabilities.py`. Do not hand-edit. "
                 "Config keys and valid values live in setup.spec.json; the API "
                 "shape is at /api/schema/ (OpenAPI). See AGENTS.md.",
        "always_included": {
            "backend_apps": ["users"],
            "auth": "Magic-link + JWT (SimpleJWT); OAuth providers optional.",
            "api_docs": "/api/schema/ (OpenAPI), /api/docs/ (Swagger UI)",
        },
        "features": features,
    }


def main() -> int:
    data = build()
    rendered = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        current = read(OUT)
        if current != rendered:
            print("capabilities.json is stale — run: python3 scripts/gen_capabilities.py",
                  file=sys.stderr)
            return 1
        print("capabilities.json is up to date.")
        return 0
    OUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(data['features'])} features).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
