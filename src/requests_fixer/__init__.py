import os
from requests_fixer.patch import patch_all, revert_all

if not os.getenv("NO_PATCH_ON_IMPORT"):
    patch_all()