# utils.py
import requests


def test_api_connection(base_url: str):
    """
    Tests basic connectivity to the API.
    Returns dict with status and details.
    """
    results = {}

    # Health check
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        results["health"] = {
            "status_code": r.status_code,
            "ok": r.ok,
        }
    except Exception as e:
        results["health"] = {"error": str(e)}
        return results

    # OpenAPI check
    try:
        r = requests.get(f"{base_url}/openapi.json", timeout=5)
        results["openapi"] = {
            "status_code": r.status_code,
            "ok": r.ok,
        }
    except Exception as e:
        results["openapi"] = {"error": str(e)}

    return results
