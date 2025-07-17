import os
import sys

class Convert:
    def get_resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        file_path = os.path.join(base_path, relative_path)
        return file_path