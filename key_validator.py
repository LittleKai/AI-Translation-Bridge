import requests


def validate_application_key():
    """Validate application key from Google Docs"""
    try:
        # Google Docs URL for key validation
        doc_url = "https://docs.google.com/document/d/1wjx-Npeoio_Hcs53mkWd-Xu0FK0d5C9QlHICYUtRs4Q/export?format=txt"

        response = requests.get(doc_url, timeout=5)

        if response.status_code == 200:
            content = response.text
            expected_key = "mzcnpXkEwW"

            if expected_key in content:
                return True, "Key validated successfully"
            else:
                return False, "Invalid key"
        else:
            return False, f"Failed to fetch key (Status: {response.status_code})"

    except Exception as e:
        return False, f"Validation error: {str(e)}"
