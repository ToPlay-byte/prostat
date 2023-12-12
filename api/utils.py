from urllib.parse import urljoin


def get_full_path(global_url: str, item_url: str) -> str:
    if item_url.startswith(('/', '...')):
        return urljoin(str(global_url), str(item_url))
    return item_url



# print(get_full_path('https://www.youtube.com/watch?v=ONcbnMX05Y0&ab_channel=MagicMusicMix', '/s/player/dee96cfa/player_ias.vflset/uk_UA/base.js'))