import json
import re
import time
import urllib.request

GITHUB_API = "https://api.github.com/repos/{repo}/releases/latest"


class UpdateCheckError(Exception):
    pass


def _parse_version(tag: str) -> tuple:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", tag)
    if not match:
        raise UpdateCheckError(f"Не вдалося розпізнати версію з тегу '{tag}'")
    return tuple(int(x) for x in match.groups())


def fetch_latest_release(repo: str, timeout: int = 10) -> dict:
    url = GITHUB_API.format(repo=repo)
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "PhotoCompressorService-UpdateChecker",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except Exception as exc:
        raise UpdateCheckError(f"Не вдалося звернутись до GitHub: {exc}") from exc

    asset = next(
        (a for a in data.get("assets", []) if a.get("name", "").lower().endswith(".exe")),
        None,
    )
    if asset is None:
        raise UpdateCheckError("У релізі немає .exe файлу інсталятора")

    return {
        "tag_name": data["tag_name"],
        "version": _parse_version(data["tag_name"]),
        "asset_name": asset["name"],
        "download_url": asset["browser_download_url"],
        "asset_size": asset["size"],
        "release_notes_url": data.get("html_url"),
    }


class UpdateCache:
    """Кешує результат перевірки, щоб не звертатись до GitHub на кожен запит /test."""

    def __init__(self):
        self._result: dict | None = None
        self._error: str | None = None
        self._checked_at: float = 0.0

    def get(self, repo: str, interval_seconds: int, force: bool = False) -> dict:
        now = time.time()
        is_fresh = (now - self._checked_at) < interval_seconds
        if not force and is_fresh and (self._result is not None or self._error is not None):
            if self._error is not None:
                raise UpdateCheckError(self._error)
            return self._result

        try:
            self._result = fetch_latest_release(repo)
            self._error = None
        except UpdateCheckError as exc:
            self._result = None
            self._error = str(exc)
            self._checked_at = now
            raise
        self._checked_at = now
        return self._result
