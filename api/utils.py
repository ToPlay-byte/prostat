from urllib.parse import urljoin


def get_full_path(global_url: str, item_url: str) -> str:
    if item_url.startswith(('/', '...')):
        return urljoin(global_url, item_url)
    return item_url

