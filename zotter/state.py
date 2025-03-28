# === GLOBAL STATE ===
from datetime import datetime

class Note:
    def __init__(self):
        self.content = [""]
        self.title = None
        self.tags = []
        self.collections = []
        self.zotero_item_key = None
        self.zotero_item_version = None
        self.last_sync_time = "Never"
        self.created_at = datetime.now().isoformat()
        self.updated_at = None

current_note = Note()
cursor_y = 0
cursor_x = 0
view_offset = 0
sync_status = ""

def word_count():
    return sum(len(line.split()) for line in current_note.content)
