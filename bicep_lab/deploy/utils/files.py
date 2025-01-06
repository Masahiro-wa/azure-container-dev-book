import os
import time
import json
import tempfile
from deploy.utils import log

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

# パラメータを一時ファイルに書き出す関数
def write_params_to_tempfile(tmp_path: str, params_dict: dict) -> str:
    temp_file = tempfile.NamedTemporaryFile(dir=tmp_path, delete=False, suffix=".json", mode="w")
    json.dump(params_dict, temp_file, indent=2)  # JSON ファイルとして書き込み
    temp_file.close()  # ファイルを閉じて保存
    time.sleep(10)  # 3秒待つ
    return temp_file.name  # ファイルパスを返す
