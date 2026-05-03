import subprocess, os

os.chdir(r'D:\ai-carbon-system')

# Add only frontend files (avoid untracked scripts)
files = [
    'frontend/src/utils/auth.js',
    'frontend/src/views/Backup.vue',
    'frontend/src/views/CarbonEntry.vue',
    'frontend/src/views/CarbonTrace.vue',
    'frontend/src/views/CarbonWizard.vue',
    'frontend/src/views/Login.vue',
]

for f in files:
    r = subprocess.run(['git', 'add', f], capture_output=True, text=True)
    print(f'git add {f}: {r.returncode}')

r = subprocess.run(['git', 'commit', '-m', 'fix: Update API base URL to Render backend'], capture_output=True, text=True, errors='replace')
print(f'Commit: {r.returncode}')
print(r.stdout)
print(r.stderr[:500] if r.stderr else '')

r = subprocess.run(['git', 'push', 'github', 'main'], capture_output=True, text=True, errors='replace')
print(f'Push: {r.returncode}')
print(r.stdout)
print(r.stderr[:1000] if r.stderr else '')