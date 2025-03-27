from datetime import datetime

def log_error(message):
    with open("zotter.log", "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")

