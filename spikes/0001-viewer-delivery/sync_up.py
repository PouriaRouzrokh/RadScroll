"""Upload a sandbox profile to the separate test AnkiWeb account (never a real one), media included.

    RADSCROLL_TEST_USER=... RADSCROLL_TEST_PW=... python3.13 -I sync_up.py <base>

The login comes from the environment and is never written to disk; the sync key is kept in the sandbox base's own
prefs (`<base>/prefs21.db`) so the sandbox Anki can sync again without a password. A full upload happens only on
the first sync, when the account is empty.
"""

import os
import sys
import time
from pathlib import Path

PACKAGES = os.environ.get("RADSCROLL_ANKI_PACKAGES", "/Applications/Anki.app/Contents/Resources/app_packages")
if PACKAGES:
    sys.path.insert(0, PACKAGES)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from anki.collection import Collection  # noqa: E402
from anki.sync_pb2 import SyncCollectionResponse  # noqa: E402
from aqt.profiles import ProfileManager  # noqa: E402

Required = SyncCollectionResponse.ChangesRequired


def sync_up(base: Path) -> None:
    user, pw = os.environ["RADSCROLL_TEST_USER"], os.environ["RADSCROLL_TEST_PW"]
    if "+radscroll" not in user:
        raise SystemExit("refusing: this script only talks to the RadScroll test account")
    col = Collection(str(base / "User 1" / "collection.anki2"))
    try:
        auth = col.sync_login(user, pw, None)
        out = col.sync_collection(auth, sync_media=False)
        print("server says:", Required.Name(out.required), "server media usn", out.server_media_usn)
        if out.new_endpoint:
            auth.endpoint = out.new_endpoint
        if out.required in (Required.FULL_UPLOAD, Required.FULL_SYNC):
            if out.server_media_usn:
                raise SystemExit("refusing a full upload: the account already holds media")
            col.close_for_full_sync()
            col.full_upload_or_download(auth=auth, server_usn=out.server_media_usn, upload=True)
            col.reopen(after_full_sync=True)
        elif out.required == Required.FULL_DOWNLOAD:
            raise SystemExit("the account wants a full download: not what this script is for")
        col.sync_media(auth)
        while col.media_sync_status().active:
            time.sleep(1)
        print("media synced:", col.media_sync_status())
    finally:
        col.close()
    pm = ProfileManager(base)
    pm.setupMeta()
    pm.load("User 1")
    pm.set_sync_key(auth.hkey)
    pm.set_sync_username(user)
    if auth.endpoint:
        pm.set_current_sync_url(auth.endpoint)
    pm.save()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    sync_up(Path(sys.argv[1]).expanduser())
