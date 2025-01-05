import os
import log

def get_file_names(dir_path: str) -> list:
    """
    Retrieves a list of file names in the specified directory.

    Args:
        dir_path (str): The path of directory.

    Returns:
        list: A list of file names in the vm_conf directory.
    """
    try:
        return [file for file in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, file))]
    except Exception as e:
        log.error(f"An error occurred while listing files in {dir_path}: {e}")
        raise e
