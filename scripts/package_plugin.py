#!/usr/bin/env python3
"""Validate the CIAD distribution contract and package the checked bytes once."""
import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
from pathlib import Path

TOOLS = {
    "search_companies", "get_company", "get_company_register_extract",
    "get_insolvency_records", "get_ai_act_timeline", "get_ai_act_article",
    "get_ai_act_penalties", "send_feedback", "list_workspace_files",
    "read_workspace_file", "get_workspace_diagnostics",
}
SKILLS = {"setup", "ai-act-prehled", "ai-smernice", "firma-podklady", "ai-ekosystem"}
FILES = {
    "plugin.json", "mcp.json", ".mcp.json", "README.md", "LICENSE",
    ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
    ".agents/plugins/marketplace.json", "assets/icon.svg", "assets/icon-512.png",
    *[f"skills/{skill}/SKILL.md" for skill in SKILLS],
}
ENDPOINT = "https://mcp.ciad.cz/mcp"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(root, name):
    return json.loads((root / name).read_text(encoding="utf-8"))


def validate(root, tag=None):
    # Distribution directories are closed: an added hook, credential or file must
    # be deliberately reviewed before the contract can allow it into the ZIP.
    for directory in ("assets", "skills", ".claude-plugin", ".agents"):
        base = root / directory
        require(base.is_dir() and not base.is_symlink(), f"Invalid directory: {directory}")
        for path in base.rglob("*"):
            name = path.relative_to(root).as_posix()
            require(not path.is_symlink(), f"Symbolic link: {name}")
            if path.is_file():
                require(name in FILES, f"Unexpected distribution file: {name}")
    for name in FILES:
        path = root / name
        require(path.is_file() and not path.is_symlink(), f"Missing or invalid file: {name}")
        require(path.stat().st_size < 5_000_000, f"Oversized file: {name}")
    portable = load(root, "plugin.json")
    require(set(portable) <= {"$schema", "name", "version", "description", "author", "homepage", "repository", "license", "keywords", "extensions"}, "Unexpected portable manifest fields")
    claude = load(root, ".claude-plugin/plugin.json")
    version = portable.get("version", "")
    require(re.fullmatch(r"\d+\.\d+\.\d+", version), "Invalid version")
    require(portable.get("name") == claude.get("name") == "ciad", "Plugin name mismatch")
    require(claude.get("version") == version, "Plugin version mismatch")
    require(tag is None or tag == f"v{version}", "Release tag mismatch")
    market = load(root, ".claude-plugin/marketplace.json")
    require(len(market.get("plugins", [])) == 1, "Expected one Claude plugin")
    item = market["plugins"][0]
    require(item.get("name") == "ciad" and item.get("version") == version and item.get("source") == "./", "Marketplace mismatch")
    for manifest in (portable, claude):
        require(manifest.get("author", {}).get("email") == "office@ciad.cz", "Support contact mismatch")
    require(market.get("owner", {}).get("email") == "office@ciad.cz", "Marketplace contact mismatch")
    mcp = load(root, "mcp.json")
    require(set(mcp) <= {"$schema", "mcpServers"}, "Unexpected MCP manifest fields")
    require(set(mcp.get("mcpServers", {})) == {"ciad"}, "Expected one MCP server")
    server = mcp["mcpServers"]["ciad"]
    require(set(server) == {"type", "url", "extensions"}, "Unexpected MCP server fields or credentials")
    require(server["type"] == "streamable-http" and server["url"] == ENDPOINT, "MCP endpoint mismatch")
    # OpenAI documents this extension; portable MCP schema 1.0.0 does not yet
    # allow it. Validate the entire explicit overlay instead of dropping OAuth.
    require(server["extensions"] == {"com.openai": {"auth": {
        "type": "oauth", "client": {"mode": "dcr"},
        "resource": ENDPOINT, "baseScopes": ["workspace:read"],
    }}}, "OAuth contract mismatch")
    require(load(root, ".mcp.json") == {"mcpServers": {"ciad": {"type": "http", "url": ENDPOINT}}}, "Claude MCP contract mismatch")
    agents = load(root, ".agents/plugins/marketplace.json")
    require(agents.get("name") == "ciad" and len(agents.get("plugins", [])) == 1, "Codex marketplace mismatch")
    require(agents["plugins"][0].get("source") == {"source": "local", "path": "./"}, "Codex plugin path mismatch")
    ext = portable.get("extensions", {}).get("com.openai", {})
    require(ext.get("onboardingSkill") == "./skills/setup/SKILL.md", "Onboarding skill mismatch")
    interface = ext.get("interface", {})
    require(0 < len(interface.get("shortDescription", "")) <= 30, "Short description invalid")
    for key in ("logo", "composerIcon"):
        require(interface.get(key) == "./assets/icon-512.png", f"Invalid {key}")
    for key, suffix in (("websiteURL", ""), ("supportURL", "/support"), ("privacyPolicyURL", "/privacy"), ("termsOfServiceURL", "/terms")):
        require(interface.get(key) == "https://mcp.ciad.cz" + suffix, f"Invalid {key}")
    cases = ext.get("review", {}).get("test_cases", {})
    require(len(cases.get("positive", [])) == 5 and len(cases.get("negative", [])) == 3, "Review scenarios mismatch")
    for case in cases["positive"]:
        require(case.get("tools_triggered") in TOOLS, "Unknown review tool")
    for caseset in cases.values():
        for case in caseset:
            require(all(isinstance(case.get(key), str) and case[key].strip() for key in ("description", "prompt", "expected_behavior")), "Incomplete review scenario")
    for skill in SKILLS:
        text = (root / f"skills/{skill}/SKILL.md").read_text(encoding="utf-8")
        require(text.startswith("---\n") and re.search(rf"^name: {re.escape(skill)}$", text, re.M), f"Invalid skill: {skill}")
        require(re.search(r"^description: .+", text, re.M), f"Missing skill description: {skill}")
    if root.parent.joinpath("src/version.ts").is_file():
        repo = root.parent
        package = load(repo, "package.json")
        lock = load(repo, "package-lock.json")
        require(package.get("version") == lock.get("version") == lock.get("packages", {}).get("", {}).get("version") == version, "Server package version mismatch")
        require(f'SERVER_VERSION = "{version}"' in (repo / "src/version.ts").read_text(), "Server runtime version mismatch")
        local = load(repo, ".claude-plugin/marketplace.json")["plugins"][0]
        require(local.get("version") == version and local.get("source") == "./plugin", "Local marketplace mismatch")
    return version


def package(root, output, tag=None):
    version = validate(root, tag)
    require(output.resolve() not in {root.joinpath(name).resolve() for name in FILES}, "Output overwrites a source file")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(FILES):
            entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, (root / name).read_bytes(), compresslevel=9)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_name("SHA256SUMS.txt").write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return {"version": version, "files": len(FILES), "bytes": output.stat().st_size, "sha256": digest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--tag")
    parser.add_argument("--tools", action="store_true")
    args = parser.parse_args()
    if args.tools:
        print(json.dumps(sorted(TOOLS)))
        return 0
    try:
        result = package(args.root, args.output, args.tag) if args.output else {"version": validate(args.root, args.tag), "files": len(FILES)}
        print(json.dumps(result, sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError):
        print("CIAD package validation failed. Check manifests, versions and distribution files.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
