import os
import uuid


class temp_data_handler(object):
    """
    This is a context manager to make sure that we remove
    the pdf file after it has been read. A simpler solution
    would be to just have a constant filename like "tmp.pdf" for
    every run, but if we ever run this asynchroniously, then
    that might cause issues.
    """

    def __init__(self, tmp_folder_name, fileroot=None, file_end=".pdf"):
        self.tmp_folder = tmp_folder_name
        if fileroot == None:
            fileroot = str(uuid.uuid4())
        self.fileroot = fileroot
        self.file_end = file_end

    def __enter__(self):
        if not os.path.exists(self.tmp_folder):
            os.makedirs(self.tmp_folder)
        self.filename = self.fileroot + self.file_end
        self.filepath = os.path.join(self.tmp_folder, self.filename)

        return self.filepath

    def __exit__(self, type, value, traceback):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
