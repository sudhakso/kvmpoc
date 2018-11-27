import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from multiprocessing import Lock


isChanged = False

class Watcher:

    DIRECTORY_TO_WATCH       = "/etc/resagent/resources/"

    def __init__(self, logger):
        self.observer = Observer()
        self.logger = logger

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(10)
#                 with Lock:
#                     if isChanged:
#                         # Raise a toast to update the content
#                         self.logger.info("Detected a change in configuration ....")
#                         isChanged = False
                self.logger.info("Watching changes %s ....", isChanged)
                isChanged = False
        except:
            self.observer.stop()
            self.logger.info("Stopping watcher")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == 'created' or event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print "Received created / modified event - %s." % event.src_path
            isChanged = True
