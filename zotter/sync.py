import requests
import traceback
from datetime import datetime
from . import state
from .log import log_error
from .config import ZOTERO_API_KEY, ZOTERO_USER_ID

def sync_to_zotero():
    state.sync_status = "[SYNCING...]"
    note = state.current_note
    note_text = "\n".join(note.content)
    html_note = "<p>" + note_text.replace("\n", "<br />") + "</p>"
    headers = {
        "Zotero-API-Key": ZOTERO_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        if note.zotero_item_key is None:
            url = f"https://api.zotero.org/users/{ZOTERO_USER_ID}/items"
            payload = [{"itemType": "note", "note": html_note}]
            r = requests.post(url, headers=headers, json=payload)
            if r.status_code in (200, 201):
                state.sync_status = "[SYNC CREATED]"
                response_data = r.json()["successful"]["0"]
                note.zotero_item_key = response_data.get("key")
                note.zotero_item_version = response_data.get("version")
                note.last_sync_time = datetime.now().strftime("%H:%M:%S")
            else:
                state.sync_status = "[SYNC FAIL]"
                log_error(f"POST failed: {r.status_code} - {r.text}")
        elif note.zotero_item_version is not None:
            url = f"https://api.zotero.org/users/{ZOTERO_USER_ID}/items/{note.zotero_item_key}"
            headers["If-Unmodified-Since-Version"] = str(note.zotero_item_version)
            payload = {
                "note": html_note
            }
            r = requests.patch(url, headers=headers, json=payload)
            if r.status_code == 204:
                state.sync_status = "[SYNC SUCCESS]"
                log_error(f"Headers after PATCH: {dict(r.headers)}")
                last_modified = r.headers.get("Last-Modified-Version")
                if last_modified is not None:
                    note.zotero_item_version = int(last_modified)
                else:
                    log_error("[WARN] Last-Modified-Version header missing in PATCH response")
                note.last_sync_time = datetime.now().strftime("%H:%M:%S")
            else:
                state.sync_status = "[SYNC FAIL]"
                log_error(f"PATCH failed: {r.status_code} - {r.text}")
        else:
            state.sync_status = "[SYNC ERROR]"
            log_error("Missing Zotero item version for update.")

    except requests.exceptions.RequestException as e:
        state.sync_status = "[SYNC ERROR]"
        log_error(f"RequestException: {str(e)}")
        if e.response:
            log_error(f"Response status: {e.response.status_code}, body: {e.response.text}")
    except Exception as e:
        state.sync_status = "[SYNC ERROR]"
        log_error(f"Exception: {type(e).__name__}: {e}")
        log_error(traceback.format_exc())
