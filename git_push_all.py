import os
import subprocess

# This script commits and pushes changes to both the outer repo and the nested repo, ensuring they are always synced!
commit_msg = input("Enter commit message: ") or "update: synchronize website updates"

# 1. Sync nested repo dating-photo-checker
nested_path = "dating-photo-checker"
if os.path.exists(nested_path):
    print("\n=============================================")
    print("Syncing nested repository (dating-photo-checker)...")
    print("=============================================")
    # Force track background images
    subprocess.run("git add -f broker-verifier/tech_bg.jpg", shell=True, cwd=nested_path)
    subprocess.run("git add -A", shell=True, cwd=nested_path)
    subprocess.run(f'git commit -m "{commit_msg}"', shell=True, cwd=nested_path)
    subprocess.run("git push origin main", shell=True, cwd=nested_path)

# 2. Sync outer repo
print("\n=============================================")
print("Syncing outer repository...")
print("=============================================")
subprocess.run("git add -f broker-verifier/tech_bg.jpg dating-photo-checker/broker-verifier/tech_bg.jpg", shell=True)
subprocess.run("git add -A", shell=True)
subprocess.run(f'git commit -m "{commit_msg}"', shell=True)
subprocess.run("git push origin main", shell=True)

print("\nAll repositories synchronized successfully!")
