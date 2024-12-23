import json
import os
import zipfile
from pathlib import Path

from tools.connect import get_models_folder
from utils import ResponseErrorHandler


class ZipOperator:
    def __init__(self, filename: str):
        self.root_path = get_models_folder()
        self.filename = filename
        self.zip_path = Path(self.root_path) / self.filename
        self.extract_path = Path(self.root_path) / self.filename.replace(".zip", "")
        self.error_handler = ResponseErrorHandler()

    def save_zip(self, file: bytes):
        self.zip_path = Path(self.root_path) / self.filename
        try:
            with open(self.zip_path, "wb") as buffer:
                buffer.write(file)

        except Exception as e:
            self.error_handler.add(
                type=self.error_handler.ERR_UNEXPECTED,
                loc=[self.error_handler.LOC_UNEXPECTED],
                msg=f"Invalid ZIP file to save. Details : {str(e)}",
                input=dict(),
            )
            raise Exception(json.dumps(self.error_handler.errors))

    def extract(self):
        try:
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                os.makedirs(self.extract_path, exist_ok=True)
                zip_ref.extractall(self.extract_path)
        except zipfile.BadZipFile as e:
            self.error_handler.add(
                type=self.error_handler.ERR_UNEXPECTED,
                loc=[self.error_handler.LOC_UNEXPECTED],
                msg=f"Invalid ZIP file to unzip. Details : {str(e)}",
                input=dict(),
            )
            raise Exception(json.dumps(self.error_handler.errors))
