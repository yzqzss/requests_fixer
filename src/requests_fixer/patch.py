# The following code will be executed when imported
import requests.cookies
import requests.utils
import http.cookiejar
import inspect
import requests
import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


replace_set_cookie_patched = False
original_set_cookie = requests.cookies.RequestsCookieJar.set_cookie
def replace_set_cookie():
    """
    - patch `requests.cookies.RequestsCookieJar.set_cookie()` to use python stdlib's `http.cookiejar.CookieJar.set_cookie()` method to avoid losing escaped quotes in cookie values.

    https://github.com/psf/requests/issues/3759
    """
    global replace_set_cookie_patched
    if replace_set_cookie_patched:
        logger.warning("replace_set_cookie() has already been patched.")
        return

    def new_set_cookie(self, cookie, *args, **kwargs):
        # return super().set_cookie(cookie, *args, **kwargs)
        return http.cookiejar.CookieJar.set_cookie(self, cookie, *args, **kwargs)

    requests.cookies.RequestsCookieJar.set_cookie = new_set_cookie
    replace_set_cookie_patched = True
def revert_replace_set_cookie():
    global replace_set_cookie_patched
    requests.cookies.RequestsCookieJar.set_cookie = original_set_cookie
    replace_set_cookie_patched = False


utf8_charset_fallback_patched = False
original_response_text = requests.Response.text
def utf8_charset_fallback(): # type: ignore
    """ 
    - patch `requests.Response.text()` to use utf-8 as fallback encoding for .text() method.

    https://github.com/psf/requests/issues/2086
    """
    global utf8_charset_fallback_patched
    if utf8_charset_fallback_patched:
        logger.warning("utf8_charset_fallback() has already been patched.")
        return

    def new_text(_self: requests.Response) -> str:
        # Handle incorrect encoding
        encoding = _self.encoding
        if encoding is None or encoding == 'ISO-8859-1':
            encoding = _self.apparent_encoding
            if encoding is None:
                encoding = 'utf-8'
        if _self.content.startswith(b'\xef\xbb\xbf'):
            content = _self.content.lstrip(b'\xef\xbb\xbf')
            encoding = "utf-8"
        else:
            content = _self.content

        try:
            return content.decode(encoding, errors="strict")
        except UnicodeDecodeError:
            raise


    requests.Response.text = property(new_text) # type: ignore
    utf8_charset_fallback_patched = True
def revert_utf8_charset_fallback(): # type: ignore
    global utf8_charset_fallback_patched
    requests.Response.text = original_response_text # type: ignore
    utf8_charset_fallback_patched = False

do_not_overwrite_auth_header_patched = False
original_get_netrc_auth = requests.utils.get_netrc_auth
def do_not_overwrite_auth_header():
    """
    - patch `requests.utils.get_netrc_auth()` to not overwrite the Authorization header with the .netrc credentials.

    https://github.com/psf/requests/issues/3929
    """
    global do_not_overwrite_auth_header_patched
    if do_not_overwrite_auth_header_patched:
        logger.warning("do_not_overwrite_auth_header() has already been patched.")
        return

    def new_get_netrc_auth(url, raise_errors=False):
        # If the Authentication tuple/object and the Authorization header have
        # not been set and the environment settings are trusted, then try to
        # create the Authentication tuple from .netrc.
        frame = inspect.currentframe()
        assert frame is not None, "UNSUPPORTED: inspect.currentframe() returned None"

        caller_frame = frame.f_back

        if caller_frame:
            caller_name = caller_frame.f_code.co_name  # get the caller function name
            logger.debug(f"get_netrc_auth() is being called by {caller_name}")
            if caller_name == "prepare_request":
                # available variables: request, self
                _request = caller_frame.f_locals["request"]
                _self = caller_frame.f_locals["self"]
                if not (("authorization" not in {header.lower() for header in _request.headers})
                    and ("authorization" not in {header.lower() for header in _self.headers})
                ):
                    return _request.auth # return the auth object as is
            elif caller_name == "rebuild_auth":
                pass # This happens within resolve_redirects()
                     # TODO: Implement this
            else:
                pass

        return original_get_netrc_auth(url, raise_errors)
    
    if inspect.currentframe() is None:
        logger.warning("UNSUPPORTED environment detected: do_not_overwrite_auth_header() patch will not be applied.")
        return

    requests.sessions.get_netrc_auth = new_get_netrc_auth
    do_not_overwrite_auth_header_patched = True
def revert_do_not_overwrite_auth_header():
    global do_not_overwrite_auth_header_patched
    requests.sessions.get_netrc_auth = original_get_netrc_auth
    do_not_overwrite_auth_header_patched = False


# https://github.com/psf/requests/issues/4926

def patch_all():
    logger.info("Applying patches...")
    replace_set_cookie()
    utf8_charset_fallback()
    do_not_overwrite_auth_header()

def revert_all():
    logger.info("Undoing patches...")
    revert_replace_set_cookie()
    revert_utf8_charset_fallback()
    revert_do_not_overwrite_auth_header()