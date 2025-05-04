from PyQt5.QtCore import QRunnable


class VolumeProcessingWorker(QRunnable):
    def __init__(self, stage, callback):
        super().__init__()
        self.stage = stage
        self.callback = callback
        self._interrupted = False

    def run(self):
        self.stage.volume_processing()  # Run processing in the background
        self.callback()  # Call the callback when finished

    def stop(self):
        self._interrupted = True