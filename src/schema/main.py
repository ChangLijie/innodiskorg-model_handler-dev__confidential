import os
from typing import Dict

from fastapi import UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator, model_validator
from tools.connect import get_models_folder
from utils.error import ResponseErrorHandler


class ResponseMessage(BaseModel):
    action: str = Field(..., description="The action being reported.")
    task_uuid: str = Field(..., description="The action uuid.")
    progress: float = Field(
        ..., description="The progress ratio as a float (e.g., 0.0 to 1.0)."
    )
    details: Dict = Field(..., description="Additional details about the response.")


class ResponseFormat(BaseModel):
    status: int = Field(..., description="The status code of the response.")
    message: ResponseMessage = Field(
        ..., description="The message object containing action, progress, and details."
    )

    @field_validator("message", mode="after")
    def convert_message_to_json(cls, value):
        value = dict(value)
        return value


# For Delete model
class DeleteModel(BaseModel):
    model: str

    @model_validator(mode="after")
    def check_file(self: "DeleteModel") -> "DeleteModel":
        error_handler = ResponseErrorHandler()

        if not self.model or not isinstance(self.model, str):
            error_handler.add(
                type=error_handler.ERR_VALIDATE,
                loc=[error_handler.LOC_BODY],
                msg="Model name is invalid or missing.",
                input={},
            )

            raise RequestValidationError(error_handler.errors)

        root_path = get_models_folder()
        model_path = os.path.join(root_path, self.model)
        if not os.path.isdir(model_path):
            error_handler.add(
                type=error_handler.ERR_VALIDATE,
                loc=[error_handler.LOC_BODY],
                msg="Model not exist.",
                input={},
            )
            raise RequestValidationError(error_handler.errors)

        return self


# For Create model
class CreateModel(BaseModel):
    model: str
    model_name_on_ollama: str

    @model_validator(mode="after")
    def check_file(self: "CreateModel") -> "CreateModel":
        error_handler = ResponseErrorHandler()

        if not self.model or not isinstance(self.model, str):
            error_handler.add(
                type=error_handler.ERR_VALIDATE,
                loc=[error_handler.LOC_BODY],
                msg="Model name is invalid or missing.",
                input={},
            )
            raise RequestValidationError(error_handler.errors)

        root_path = get_models_folder()
        model_path = os.path.join(root_path, self.model)
        if not os.path.isdir(model_path):
            error_handler.add(
                type=error_handler.ERR_VALIDATE,
                loc=[error_handler.LOC_BODY],
                msg="Model not exist.",
                input={},
            )
            raise RequestValidationError(error_handler.errors)

        return self


class DeployModel(BaseModel):
    model: UploadFile
    model_name_on_ollama: str

    @model_validator(mode="after")
    def check_schema(self: "UploadModel") -> "UploadModel":
        error_handler = ResponseErrorHandler()

        if self.model.content_type != "application/zip":
            error_handler.add(
                type=error_handler.ERR_VALIDATE,
                loc=[error_handler.LOC_BODY],
                msg="'content_type' must be 'application/zip'",
                input={"model": self.model.content_type},
            )
            raise RequestValidationError(error_handler.errors)
        if self.model.file._file:
            self.model.file._file.seek(0, 2)
            file_size = self.model.file._file.tell()
            self.model.file._file.seek(0)
            if file_size == 0:
                error_handler.add(
                    type=error_handler.ERR_VALIDATE,
                    loc=[error_handler.LOC_BODY],
                    msg="Upload file is empty.",
                    input={"file_size": file_size},
                )
                raise RequestValidationError(error_handler.errors)
        return self


# For Upload model
class UploadModel(BaseModel):
    model: UploadFile

    @model_validator(mode="after")
    def check_schema(self: "UploadModel") -> "UploadModel":
        error_handler = ResponseErrorHandler()

        if self.model.content_type != "application/zip":
            error_handler.add(
                type=error_handler.ERR_VALIDATE,
                loc=[error_handler.LOC_BODY],
                msg="'content_type' must be 'application/zip'",
                input={"model": self.model.content_type},
            )
            raise RequestValidationError(error_handler.errors)
        if self.model.file._file:
            self.model.file._file.seek(0, 2)
            file_size = self.model.file._file.tell()
            self.model.file._file.seek(0)
            if file_size == 0:
                error_handler.add(
                    type=error_handler.ERR_VALIDATE,
                    loc=[error_handler.LOC_BODY],
                    msg="Upload file is empty.",
                    input={"file_size": file_size},
                )
                raise RequestValidationError(error_handler.errors)
        return self
