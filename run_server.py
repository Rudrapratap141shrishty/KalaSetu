"""
Unified Launcher for KalaSetu (कला सेतु) - AI-Driven Artisan Market Linkage & Smart Cataloging Mobile App
Initializes databases (SQLite + MongoDB Vault), performs auto-migrations, seeds data, and launches the Django web server.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / 'backend'
PORT = 8000

def run_command(cmd, cwd=None):
    print(f"[Launcher] Executing: {cmd}")
    subprocess.run(cmd, shell=True, cwd=cwd or BACKEND_DIR, check=True)

def main():
    print("=" * 65)
    print("  KalaSetu (कला सेतु) - AI Market Linkage for Marginalized Artisans")
    print("  Smart Cataloging • GraphQL • REST API • Multi-DB • UPI Payments")
    print("=" * 65)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artisan_core.settings')
    sys.path.insert(0, str(BACKEND_DIR))
    
    # 1. Run migrations
    try:
        print("[Launcher] Checking database schemas & applying migrations...")
        run_command("python manage.py makemigrations artisans_app")
        run_command("python manage.py migrate")
    except Exception as e:
        print(f"[Launcher Warning] Migration status: {e}")

    # 2. Seed initial data
    try:
        print("[Launcher] Ensuring authentic seed data is loaded...")
        run_command('python manage.py shell -c "from artisans_app.mock_seed import seed_database; seed_database()"')
    except Exception as e:
        print(f"[Launcher Warning] Seed status: {e}")

    # 3. Start server
    print("\n" + "=" * 65)
    print(f"  ✨ Mobile Application Running at:  http://localhost:{PORT}/")
    print(f"  ◈  Interactive GraphQL Explorer:  http://localhost:{PORT}/graphql")
    print(f"  ⚡ REST API Base Endpoint:         http://localhost:{PORT}/api/v1/")
    print(f"  🍃 MongoDB Document Vault:        http://localhost:{PORT}/api/v1/mongo/vault/")
    print(f"  🛡️ Django Admin Portal:           http://localhost:{PORT}/admin/")
    print("=" * 65 + "\n")

    run_command(f"python manage.py runserver 0.0.0.0:{PORT}")

if __name__ == '__main__':
    main()
