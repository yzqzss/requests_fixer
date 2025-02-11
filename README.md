# requests_fixer

> I don't need buggy behavior forward-compatibility.

"Fixed" bugs:

- [Remove ISO-8859-1 charset fallback · Issue #2086](https://github.com/psf/requests/issues/2086)
- [cookies.py why replace escaped quote with nothing? · Issue #3759](https://github.com/psf/requests/issues/3759)
- [Don't override `Authorization` header when contents are bearer token (or any other token) · Issue #3929](https://github.com/psf/requests/issues/3929)

<!--

Planned:

- [Request with data which consists of empty values only sends bad request by romanyakovlev · Pull Request #6122](https://github.com/psf/requests/pull/6122)
- [Session.verify=False ignored when REQUESTS_CA_BUNDLE environment variable is set · Issue #3829](https://github.com/psf/requests/issues/3829)
- [Make response.next lazily computable. · Issue #4123](https://github.com/psf/requests/issues/4123) 

-->

## Installation

```bash
pip install requests_fixer
```

## Usage

```python
import requests_fixer # yeap, that's it, just import it
```

> To disable the auto patching on import, set the `NO_PATCH_ON_IMPORT` environment variable.

If you want to undo the patches:

```python
requests_fixer.revert_all()
```
