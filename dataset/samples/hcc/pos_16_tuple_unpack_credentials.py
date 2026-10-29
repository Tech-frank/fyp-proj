import requests

BASE = "https://intranet.example.com/api"
username, password = "svc_reports", "Rep0rts!Svc#88"


def fetch_report(report_id):
    r = requests.get(f"{BASE}/reports/{report_id}", auth=(username, password), timeout=15)
    r.raise_for_status()
    return r.json()
