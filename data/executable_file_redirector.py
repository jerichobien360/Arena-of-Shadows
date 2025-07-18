import os
import sys

class Convert:

    """
    Handles resource path resolution for bundled or local execution environments.

    This class is especially useful when working with PyInstaller or similar tools
    that bundle Python applications. It ensures that resource files (like images,
    configs, etc.) are correctly located whether the app is run as a script or as
    a standalone executable.
    """

    def get_resource_path(self, relative_path):
        
        # Resolves resource path for both bundled executables and local scripts.        
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        file_path = os.path.join(base_path, relative_path)
        return file_path