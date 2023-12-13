from typing import Optional

import requests

from urllib.parse import urljoin


def get_full_path(global_url: str, item_url: str) -> str:
    if item_url.startswith(('/', '...')):
        return urljoin(str(global_url), str(item_url))
    return item_url


def get_request_content(url: str) -> Optional[str]:
    try:
        req = requests.get(url, timeout=3)
    except (requests.exceptions.SSLError, requests.exceptions.ConnectTimeout):
        return None
    else:
        return req.text
