from watchdog.events import FileSystemEventHandler

class NewImageHandler(FileSystemEventHandler):
    def __init__(self, correct_image_paths, output_folder, similarity_check_func):
        self.correct_image_paths = correct_image_paths
        self.output_folder = output_folder
        self.similarity_check_func = similarity_check_func

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            new_image_path = event.src_path
            self.similarity_check_func(self.correct_image_paths, new_image_path, self.output_folder)
