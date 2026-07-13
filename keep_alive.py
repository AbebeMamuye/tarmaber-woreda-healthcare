"""
Supabase Keep-Alive Script
═══════════════════════════
Prevents your free-tier Supabase project from auto-pausing after 7 days
of inactivity by sending a lightweight heartbeat query.

Usage:
  1. ONE-SHOT:   python keep_alive.py
  2. CONTINUOUS:  python keep_alive.py --loop
     (sends a heartbeat every 4 days automatically)
  3. CRON JOB:    Schedule the one-shot command externally (e.g. cron-job.org)

Environment Variables (optional — hardcoded fallbacks are included):
  SUPABASE_URL  – Your Supabase project URL
  SUPABASE_KEY  – Your Supabase anon/public key
"""

import requests
import os
import sys
import socket
import time
import argparse
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
# Fallback credentials (same as app.py) — env vars take priority
FALLBACK_URL = "https://etmvricanlatzhrwlsvx.supabase.co"
FALLBACK_KEY = "sb_publishable_b1RPpHyaAA2_kXhiFame1A_O41Ds3IE"

LOOP_INTERVAL_DAYS = 4          # Send heartbeat every 4 days (pause happens at 7)
MAX_RETRIES        = 3          # Retry on failure
RETRY_DELAY_SEC    = 30         # Base delay between retries (doubles each attempt)
REQUEST_TIMEOUT    = 15         # HTTP timeout in seconds


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _get_credentials():
    """Resolve Supabase URL and KEY from env vars or fallback."""
    url = os.getenv("SUPABASE_URL") or FALLBACK_URL
    key = os.getenv("SUPABASE_KEY") or FALLBACK_KEY

    if not url or not key:
        print(f"[{_timestamp()}] ❌ SUPABASE_URL or SUPABASE_KEY not configured.")
        sys.exit(1)

    return url.rstrip("/"), key


def _dns_check(url: str) -> bool:
    """Check if the Supabase hostname resolves in DNS."""
    hostname = url.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        ip = socket.gethostbyname(hostname)
        print(f"[{_timestamp()}] [OK] DNS OK — {hostname} → {ip}")
        return True
    except socket.gaierror:
        print(f"[{_timestamp()}] [ERROR] DNS FAILED — '{hostname}' not found.")
        print(f"[{_timestamp()}] [INFO] The project might be PAUSED. Please Resume it in the Supabase dashboard.")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# HEARTBEAT
# ─────────────────────────────────────────────────────────────────────────────
def send_heartbeat(url: str, key: str) -> bool:
    """
    Send a lightweight SELECT query to Supabase to keep the project active.
    Returns True on success, False on failure.
    """
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }
    endpoint = f"{url}/rest/v1/performance_data?select=woreda_name&limit=1"

    for attempt in range(1, MAX_RETRIES + 1):
        delay = RETRY_DELAY_SEC * (2 ** (attempt - 1))  # Exponential backoff
        try:
            print(f"[{_timestamp()}] [INFO] Heartbeat attempt {attempt}/{MAX_RETRIES} -> {url}")
            resp = requests.get(endpoint, headers=headers, timeout=REQUEST_TIMEOUT)

            if resp.status_code == 200:
                rows = resp.json()
                row_count = len(rows) if isinstance(rows, list) else "?"
                print(f"[{_timestamp()}] [SUCCESS] Heartbeat SUCCESS — HTTP 200, {row_count} row(s) returned.")
                return True

            elif resp.status_code == 401:
                print(f"[{_timestamp()}] [ERROR] AUTH ERROR (401) — API key is invalid or expired.")
                print(f"[{_timestamp()}] [INFO] Please check your API key in the Supabase dashboard.")
                return False  # No point retrying auth errors

            elif resp.status_code == 404:
                print(f"[{_timestamp()}] [WARN] TABLE NOT FOUND (404) — 'performance_data' table may not exist.")
                print(f"[{_timestamp()}] [INFO] However, the project is ACTIVE and won't be paused.")
                return True  # Project is alive even if table doesn't exist

            elif resp.status_code in (502, 503, 521):
                print(f"[{_timestamp()}] [WAIT] Server waking up (HTTP {resp.status_code}). Retrying in {delay}s...")
                time.sleep(delay)
                continue

            else:
                print(f"[{_timestamp()}] [WARN] Unexpected HTTP {resp.status_code}: {resp.text[:200]}")
                if attempt < MAX_RETRIES:
                    print(f"[{_timestamp()}] [RETRY] Retrying in {delay}s...")
                    time.sleep(delay)

        except requests.exceptions.ConnectionError as e:
            print(f"[{_timestamp()}] [ERROR] Connection Error: {e}")
            if attempt < MAX_RETRIES:
                print(f"[{_timestamp()}] [RETRY] Retrying in {delay}s...")
                time.sleep(delay)

        except requests.exceptions.Timeout:
            print(f"[{_timestamp()}] [ERROR] Request timed out after {REQUEST_TIMEOUT}s.")
            if attempt < MAX_RETRIES:
                print(f"[{_timestamp()}] [RETRY] Retrying in {delay}s...")
                time.sleep(delay)

        except Exception as e:
            print(f"[{_timestamp()}] [ERROR] Unexpected error: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(delay)

    print(f"[{_timestamp()}] [ERROR] All {MAX_RETRIES} attempts failed.")
    return False


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def keep_alive(loop: bool = False):
    """Run heartbeat once, or in a continuous loop."""
    url, key = _get_credentials()

    print("=" * 60)
    print(f"  Supabase Keep-Alive  |  {_timestamp()}")
    print(f"  Project: {url}")
    print(f"  Mode: {'[LOOP] CONTINUOUS (every {0} days)'.format(LOOP_INTERVAL_DAYS) if loop else '[ONCE] ONE-SHOT'}")
    print("=" * 60)

    while True:
        # Step 1: DNS check
        if not _dns_check(url):
            print(f"[{_timestamp()}] [WARN] DNS failed — Please Resume the project in Supabase dashboard and try again.")
            if not loop:
                sys.exit(1)
            print(f"[{_timestamp()}] [RETRY] Will retry in {LOOP_INTERVAL_DAYS} days...")
            time.sleep(LOOP_INTERVAL_DAYS * 86400)
            continue

        # Step 2: Send heartbeat
        success = send_heartbeat(url, key)

        if not loop:
            sys.exit(0 if success else 1)

        # Step 3: Sleep until next heartbeat
        next_run = LOOP_INTERVAL_DAYS * 86400  # days → seconds
        hours = next_run / 3600
        print(f"[{_timestamp()}] [SLEEP] Sleeping for {LOOP_INTERVAL_DAYS} days ({hours:.0f} hours)...")
        print(f"[{_timestamp()}] [NEXT] Next heartbeat at ~{datetime.fromtimestamp(time.time() + next_run).strftime('%Y-%m-%d %H:%M')}")
        print("-" * 60)
        time.sleep(next_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supabase Keep-Alive Heartbeat")
    parser.add_argument(
        "--loop", action="store_true",
        help=f"Run continuously, sending a heartbeat every {LOOP_INTERVAL_DAYS} days."
    )
    args = parser.parse_args()
    keep_alive(loop=args.loop)
