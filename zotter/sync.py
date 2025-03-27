import time
import requests
import traceback
from datetime import datetime
from .state import note_content, zotero_item_key, zotero_item_version, last_sync_time, last_sync
from .log import log_error
from .config import ZOTERO_API_KEY, ZOTERO_USER_ID, sync_interval

sync_status = ""

def sync_to_zotero():
    global sync_status, zotero_item_key, zotero_item_version, last_sync_time
    sync_status = "[SYNCING...]"
    note_text = "\n".join(note_content)
    html_note = "<p>" + note_text.replace("\n", "<br />") + "</p>"
    headers = {
        "Zotero-API-Key": ZOTERO_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        if zotero_item_key is None:
            url = f"https://api.zotero.org/users/{ZOTERO_USER_ID}/items"
            payload = [{"itemType": "note", "note": html_note}]
            r = requests.post(url, headers=headers, json=payload)
            if r.status_code in (200, 201):
                sync_status = "[SYNC CREATED]"
                response_data = r.json()["successful"]["0"]
                zotero_item_key = response_data.get("key")
                zotero_item_version = response_data.get("version")
                last_sync_time = datetime.now().strftime("%H:%M:%S")
            else:
                sync_status = "[SYNC FAIL]"
                log_error(f"POST failed: {r.status_code} - {r.text}")
        elif zotero_item_version is not None:
            url = f"https://api.zotero.org/users/{ZOTERO_USER_ID}/items/{zotero_item_key}"
            headers["If-Unmodified-Since-Version"] = str(zotero_item_version)
            payload = {
                "note": html_note
            }
            r = requests.patch(url, headers=headers, json=payload)
            if r.status_code == 204:
                sync_status = "[SYNC SUCCESS]"
                log_error(f"Headers after PATCH: {dict(r.headers)}")
                last_modified = r.headers.get("Last-Modified-Version")
                if last_modified is not None:
                    zotero_item_version = int(last_modified)
                else:
                    log_error("[WARN] Last-Modified-Version header missing in PATCH response")
                last_sync_time = datetime.now().strftime("%H:%M:%S")
            else:
                sync_status = "[SYNC FAIL]"
                log_error(f"PATCH failed: {r.status_code} - {r.text}")
        else:
            sync_status = "[SYNC ERROR]"
            log_error("Missing Zotero item version for update.")

    except requests.exceptions.RequestException as e:
        sync_status = "[SYNC ERROR]"
        log_error(f"RequestException: {str(e)}")
        if e.response:
            log_error(f"Response status: {e.response.status_code}, body: {e.response.text}")
    except Exception as e:
        sync_status = "[SYNC ERROR]"
        log_error(f"Exception: {type(e).__name__}: {e}")
        log_error(traceback.format_exc())

def periodic_sync():
    global last_sync
    while True:
        if zotero_item_key is not None and time.time() - last_sync >= sync_interval:
            sync_to_zotero()
            last_sync = time.time()
        time.sleep(5)
