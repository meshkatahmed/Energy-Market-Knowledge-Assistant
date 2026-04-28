import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.core.config import settings
from app.services.vector_store import vector_store_service

class RawDataHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()

    def on_any_event(self, event):
        if event.is_directory:
            return
        
        # Filter for supported types
        if event.src_path.endswith(('.pdf', '.csv', '.xlsx', '.docx', '.txt')):
            with self.lock:
                print(f"\n>> [WATCHER] Change detected: {os.path.basename(event.src_path)}")
                try:
                    vector_store_service.build_database(settings.DATA_DIR)
                except Exception as e:
                    print(f">> [WATCHER] Error: {e}")

def get_watcher_observer():
    event_handler = RawDataHandler()
    observer = Observer()
    observer.schedule(event_handler, settings.DATA_DIR, recursive=False)
    return observer
