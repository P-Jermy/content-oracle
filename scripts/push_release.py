#!/usr/bin/env python3
"""Push content-oracle to GitHub via API"""
import subprocess, json, base64, os

REPO = "P-Jermy/content-oracle"
BASE = "/home/jermy/content-oracle"

def gh_post(path, data):
    cmd = ["gh", "api", path, "--method", "POST", "--input", "-"]
    r = subprocess.run(cmd, input=json.dumps(data).encode(), capture_output=True, timeout=30)
    if r.returncode != 0:
        print(f"ERR [{path}]: {r.stderr.decode()[:200]}")
        return None
    return json.loads(r.stdout)

def gh_patch(path, data):
    cmd = ["gh", "api", path, "--method", "PATCH", "--input", "-"]
    r = subprocess.run(cmd, input=json.dumps(data).encode(), capture_output=True, timeout=30)
    if r.returncode != 0:
        print(f"ERR [{path}]: {r.stderr.decode()[:200]}")
        return None
    return json.loads(r.stdout)

def gh_get(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, timeout=15)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout) if r.stdout else {}

# Step 1: Get parent commit tree
parent = gh_get(f"repos/{REPO}/git/refs/heads/main")
if not parent:
    print("No parent ref")
    exit(1)
parent_sha = parent["object"]["sha"]
commit = gh_get(f"repos/{REPO}/git/commits/{parent_sha}")
base_tree = commit["tree"]["sha"]
print(f"Parent: {parent_sha}  Tree: {base_tree}")

# Step 2: Collect files
files = []
for root, dirs, fnames in os.walk(BASE):
    dirs[:] = [d for d in dirs if d != ".git" and not d.endswith("__pycache__")]
    for f in fnames:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, BASE)
        files.append((rel, full))
files.sort()
print(f"Files: {len(files)}")

# Step 3: Create blobs
blobs = []
for rel, full in files:
    with open(full, "rb") as f:
        content = f.read()
    if not content:
        continue
    data = {"content": base64.b64encode(content).decode(), "encoding": "base64"}
    blob = gh_post(f"repos/{REPO}/git/blobs", data)
    if blob and "sha" in blob:
        blobs.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        print(f"  ✓ {rel}")
    else:
        print(f"  ✗ {rel}")

if len(blobs) != len(files):
    print(f"Only {len(blobs)}/{len(files)} blobs created. Aborting.")
    exit(1)

# Step 4: Create tree
tree = gh_post(f"repos/{REPO}/git/trees", {"tree": blobs, "base_tree": base_tree})
if not tree or "sha" not in tree:
    print("Tree creation failed")
    exit(1)
print(f"Tree: {tree['sha']}")

# Step 5: Create commit
msg = "feat: 重写 trends 匹配原版 cheat-on-content 架构"
commit = gh_post(f"repos/{REPO}/git/commits", {
    "message": msg,
    "tree": tree["sha"],
    "parents": [parent_sha]
})
if not commit or "sha" not in commit:
    print("Commit creation failed")
    exit(1)
print(f"Commit: {commit['sha']}")

# Step 6: Update ref
result = gh_patch(f"repos/{REPO}/git/refs/heads/main", {"sha": commit["sha"], "force": False})
if result:
    print(f"\n✅ Pushed! https://github.com/{REPO}")
else:
    print("\n✗ Push failed")
