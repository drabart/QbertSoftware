import os
from ament_index_python.packages import get_package_share_directory

SHARE_DIR = get_package_share_directory("qbert_gui")

def get_from_shared(path: str):
    return os.path.join(SHARE_DIR, path) 
