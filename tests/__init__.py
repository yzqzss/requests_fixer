import requests

from requests.cookies import create_cookie

import requests_fixer.patch

def test_replace_set_cookie():
    EXPECTED_BEFORE = '"123456"'
    EXPECTED_AFTER = '"123\\"456"'
    # Create a cookie with escaped quotes
    def before():
        s = requests.Session()
        cookie = create_cookie(
            name="test_cookie",
            value='"123\\"456"',
        )
        s.cookies.set_cookie(cookie)
        got = s.cookies.get("test_cookie")
        assert got == EXPECTED_BEFORE, f"Expected {EXPECTED_BEFORE}, got {got}"
    def after():
        s = requests.Session()
        cookie = create_cookie(
            name="test_cookie",
            value='"123\\"456"',
        )
        s.cookies.set_cookie(cookie)
        got = s.cookies.get("test_cookie")
        assert got == EXPECTED_AFTER, f"Expected {EXPECTED_AFTER}, got {got}"

    before()
    requests_fixer.patch.replace_set_cookie()
    after()
    requests_fixer.patch.revert_replace_set_cookie()
    before()

def test_do_not_overwrite_auth_header():
    from pathlib import Path
    netrc_path = Path("~/.netrc").expanduser()
    exists = netrc_path.exists()
    original = netrc_path.read_bytes() if exists else b""
    netrc_path.write_text("machine example.com login user password pass\n")

    try:
        s = requests.Session()
        r = s.get("https://example.com")
        assert r.request.headers["Authorization"] == "Basic dXNlcjpwYXNz", r.request.headers["Authorization"]

        r = s.get("https://example.com", auth=("newuser", "newpass"))
        assert r.request.headers["Authorization"] == "Basic bmV3dXNlcjpuZXdwYXNz", r.request.headers["Authorization"]

        r = s.get("https://example.com", headers={"Authorization": "Basic aaaaa"})
        assert r.request.headers.get("Authorization") == "Basic dXNlcjpwYXNz", r.request.headers["Authorization"]

        requests_fixer.patch.do_not_overwrite_auth_header()

        r = s.get("https://example.com")
        assert r.request.headers["Authorization"] == "Basic dXNlcjpwYXNz", r.request.headers["Authorization"]

        r = s.get("https://example.com", auth=("newuser", "newpass"))
        assert r.request.headers.get("Authorization") == "Basic bmV3dXNlcjpuZXdwYXNz", r.request.headers["Authorization"]

        r = s.get("https://example.com", headers={"Authorization": "Basic aaaaa"})
        assert r.request.headers.get("Authorization") == "Basic aaaaa", r.request.headers["Authorization"]  # patched

        requests_fixer.patch.revert_do_not_overwrite_auth_header()

        r = s.get("https://example.com", headers={"Authorization": "Basic aaaaa"})
        assert r.request.headers.get("Authorization") == "Basic dXNlcjpwYXNz", r.request.headers["Authorization"]

    finally:
        if exists:
            netrc_path.write_bytes(original) # Restore original .netrc
        else:
            netrc_path.unlink()

if __name__ == "__main__":
    requests_fixer.revert_all()

    test_replace_set_cookie()
    test_do_not_overwrite_auth_header()

    requests_fixer.patch_all()