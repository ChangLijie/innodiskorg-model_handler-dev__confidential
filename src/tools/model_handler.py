import asyncio
import json
import os
import shutil
from string import Template

import httpx
from fastapi import UploadFile
from schema.main import ResponseFormat, ResponseMessage
from tools.connect import get_model_server_url, get_models_folder
from utils import ResponseErrorHandler, config_logger, get_uuid

from .zip_handler import ZipOperator

MODEL_STATUS = {}


class CustomError(Exception):
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details


class ModelOperator:
    def __init__(self):
        self.uuid = get_uuid()
        # manager.create_room(self.uuid)
        self.root_path = get_models_folder()
        self.message = asyncio.Queue()
        self.alive = True
        self.model_status = MODEL_STATUS
        self.error_handler = ResponseErrorHandler()
        self.log = config_logger(
            file_name=f"{self.uuid}.log",
            write_mode="w",
            level="debug",
            logger_name=f"{self.uuid}_logger",
            sub_folder="tasks",
        )

    async def delete_model(self, model: str):
        try:
            self.model_status[model] = self.uuid
            self.log.info(f"'{self.uuid}'Delete model.Details : {model}")
            model_path = os.path.join(self.root_path, model)
            response = ResponseFormat(
                status=200,
                message=ResponseMessage(
                    action="Start delete model.",
                    task_uuid=str(self.uuid),
                    progress=0.5,
                    details={"model_name": model},
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")

            shutil.rmtree(model_path)

            response = ResponseFormat(
                status=200,
                message=ResponseMessage(
                    action="Success delete model.",
                    task_uuid=str(self.uuid),
                    progress=1,
                    details={"model_name": model},
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")

            self.log.warning(f"'{self.uuid}'Delete model success.Details : {model}.")

        except Exception as e:
            self.log.error(f"'{self.uuid}' Failed Delete model list. Details: {e}")
            self.error_handler.add(
                type=self.error_handler.ERR_INTERNAL,
                loc=[self.error_handler.ERR_INTERNAL],
                msg=str(f"'{self.uuid}' Failed Delete model list. Details: {e}"),
                input=dict(),
            )

            response = ResponseFormat(
                status=500,
                message=ResponseMessage(
                    action="Failed delete model.",
                    task_uuid=str(self.uuid),
                    progress=-1,
                    details=dict(self.error_handler.errors[0]),
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")

        finally:
            del self.model_status[model]
            self.alive = False

    async def get_status(self):
        while self.alive or not self.message.empty():
            if not self.message.empty():
                raw_message = await self.message.get()
                try:
                    if isinstance(raw_message, str):
                        message = json.loads(raw_message)
                    elif isinstance(raw_message, dict):
                        message = raw_message
                    else:
                        raise TypeError(
                            f"Unsupported message type: {type(raw_message)}"
                        )
                    await asyncio.sleep(0.01)
                    yield message["status"], message["message"]
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    self.log.error(
                        f"Failed to process message: {raw_message}, Error: {e}"
                    )
                    yield 500, {"error": "Invalid message format"}

    async def get_model_list(self):
        try:
            total_model_dir = next(os.walk(self.root_path))[1]

            self.log.info(f"'{self.uuid}'Get model list. Detail:{total_model_dir}")
            total_model = len(total_model_dir)
            for progress, model in enumerate(total_model_dir):
                response = ResponseFormat(
                    status=200,
                    message=ResponseMessage(
                        action="Get model.",
                        task_uuid=str(self.uuid),
                        progress=(progress + 1) / total_model,
                        details={"model": model},
                    ),
                )
                await self.message.put(json.dumps(dict(response)) + "\n")

        except Exception as e:
            self.log.error(f"'{self.uuid}' Failed Get model list. Details: {e}")
            self.error_handler.add(
                type=self.error_handler.ERR_INTERNAL,
                loc=[self.error_handler.ERR_INTERNAL],
                msg=str(f"'{self.uuid}' Failed Get model list. Details: {e}"),
                input=dict(),
            )

            response = ResponseFormat(
                status=500,
                message=ResponseMessage(
                    action="Failed to get model list.",
                    task_uuid=str(self.uuid),
                    progress=-1,
                    details=dict(self.error_handler.errors[0]),
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")

        finally:
            self.alive = False

    async def save_model(
        self,
        model: str,
        file: UploadFile,
        progress_ratio: float = 1,
        progress_base: float = 0,
    ):
        # async def save_model(self, model: str, file: UploadFile, content_length: int):
        try:
            processed_size = 0

            self.model_status[model] = self.uuid

            operator = ZipOperator(filename=model)
            self.log.info(f"'{self.uuid}' Start to save '{model}'.")
            response = ResponseFormat(
                status=200,
                message=ResponseMessage(
                    action="Started save model.",
                    task_uuid=str(self.uuid),
                    progress=progress_ratio * 0 + progress_base,
                    details={"model": model},
                ),
            )

            processed_size = 0
            chunk_size = 1024 * 1024
            total = file.size
            with open(operator.zip_path, "wb") as buffer:
                file.file.seek(0)
                while True:
                    chunk = file.file.read(chunk_size)
                    if not chunk:
                        break
                    buffer.write(chunk)
                    processed_size = processed_size + chunk_size

                    if processed_size >= total:
                        processed_size = total

                    progress = round(0.5 * (processed_size / total), 2)

                    response = ResponseFormat(
                        status=200,
                        message=ResponseMessage(
                            action=f"Saving '{model}'.",
                            task_uuid=str(self.uuid),
                            progress=progress_ratio * progress + progress_base,
                            details={"model": model},
                        ),
                    )
                    await self.message.put(json.dumps(dict(response)) + "\n")

                # with open(self.zip_path, "wb") as buffer:
                #     buffer.write(file)

            self.log.info(f"'{self.uuid}' Save '{model}' success.")
            response = ResponseFormat(
                status=200,
                message=ResponseMessage(
                    action=f"Save '{model}' success.",
                    task_uuid=str(self.uuid),
                    progress=progress_ratio * 0.5 + progress_base,
                    details={"model": model},
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")

            response = ResponseFormat(
                status=200,
                message=ResponseMessage(
                    action="Start extracted model.",
                    task_uuid=str(self.uuid),
                    progress=progress_ratio * 0.6 + progress_base,
                    details={"model": model},
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")

            operator.extract()

            for root, _, files in os.walk(operator.extract_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file)
                    if ext.lower() != ".gguf":
                        self.log.error(
                            f"'{self.uuid}' Failed to save model. Details: Invalid file extension '{ext}' for file '{file_path}'."
                        )
                        shutil.rmtree(root)
                        raise ValueError(
                            f"Invalid file extension '{ext}' for file '{file_path}'."
                        )

            self.log.info(f"'{self.uuid}' Upload '{model}' success.")

            response = ResponseFormat(
                status=200,
                message=ResponseMessage(
                    action="Success upload model file.",
                    task_uuid=str(self.uuid),
                    progress=progress_ratio * 1 + progress_base,
                    details={"model": model},
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")

        except Exception as e:
            self.log.error(f"'{self.uuid}' Failed save model. Details: {e}")
            self.error_handler.add(
                type=self.error_handler.ERR_INTERNAL,
                loc=[self.error_handler.ERR_INTERNAL],
                msg=str(f"'{self.uuid}' Failed save model. Details: {e}"),
                input=dict(),
            )

            response = ResponseFormat(
                status=500,
                message=ResponseMessage(
                    action="Failed to upload model.",
                    task_uuid=str(self.uuid),
                    progress=-1,
                    details=dict(self.error_handler.errors[0]),
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")
            return False
        finally:
            self.alive = False
            del self.model_status[model]

    async def create_model(
        self,
        model: str,
        model_name_on_ollama: str,
        progress_ratio: float = 1,
        progress_base: float = 0,
    ):
        try:
            self.model_status[model] = self.uuid
            model_server_url = get_model_server_url()
            url = model_server_url + "api/create"
            model_folder = os.path.join(self.root_path, model)
            self.log.debug(f"'{self.uuid}' Started created model {model} ")
            ollama_model_folder = os.path.join(
                "/home", model
            )  # Check if the model folder exists
            response = ResponseFormat(
                status=200,
                message=ResponseMessage(
                    action="Started to create model.",
                    task_uuid=str(self.uuid),
                    progress=progress_ratio * 0.1 + progress_base,
                    details={"model": model},
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")

            if not os.path.exists(model_folder):
                self.log.warning(
                    f"'{self.uuid}' Create model error. Details : {model} not exist."
                )

                self.error_handler.add(
                    type=self.error_handler.ERR_INTERNAL,
                    loc=[self.error_handler.ERR_INTERNAL],
                    msg=f"'{self.uuid}' Create model error. Details : {model} not exist.",
                    input=dict(),
                )
                raise CustomError(
                    message="Create model error.",
                    details=self.error_handler.errors[0],
                )
                response = ResponseFormat(
                    status=500,
                    message=ResponseMessage(
                        action="Create model error.",
                        task_uuid=str(self.uuid),
                        progress=-1,
                        details=dict(self.error_handler.errors),
                    ),
                )
                await self.message.put(json.dumps(dict(response)) + "\n")
                return
            self.log.debug(f"'{self.uuid}'Start structure template ")
            self.log.debug(
                f"'{self.uuid}'Start structure template model_folder :{model_folder}"
            )
            response = ResponseFormat(
                status=200,
                message=ResponseMessage(
                    action="Start structure template",
                    task_uuid=str(self.uuid),
                    progress=progress_ratio * 0.2 + progress_base,
                    details={"model": model},
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")

            files = next(os.walk(model_folder))[2]

            modelfile_content = ""
            basemodel_template = Template("FROM $base_model_path")
            gguf_template = Template("\nADAPTER $gguf_path")

            # Prepare the modelfile content
            if len(files) == 2:
                if "lora" in files[0]:
                    base_model_path = os.path.join(ollama_model_folder, files[1])
                    gguf_path = os.path.join(ollama_model_folder, files[0])
                else:
                    base_model_path = os.path.join(ollama_model_folder, files[0])
                    gguf_path = os.path.join(ollama_model_folder, files[1])

                modelfile_content = basemodel_template.substitute(
                    base_model_path=base_model_path
                ) + gguf_template.substitute(gguf_path=gguf_path)
            elif len(files) == 1:
                base_model_path = os.path.join(ollama_model_folder, files[0])
                modelfile_content = basemodel_template.substitute(
                    base_model_path=base_model_path
                )
            else:
                self.error_handler.add(
                    type=self.error_handler.ERR_INTERNAL,
                    loc=[self.error_handler.ERR_INTERNAL],
                    msg=f"'{self.uuid}' Create model error. Details : File nums in {model} folder is illegal.",
                    input=dict(),
                )
                raise CustomError(
                    message="Create model error.",
                    details=self.error_handler.errors[0],
                )
                response = ResponseFormat(
                    status=500,
                    message=ResponseMessage(
                        action="Failed to structure template",
                        task_uuid=str(self.uuid),
                        progress=-1,
                        details=dict(self.error_handler.errors),
                    ),
                )
                await self.message.put(json.dumps(dict(response)) + "\n")
                return
            # Prepare payload
            payload = {
                "model": model_name_on_ollama,
                "modelfile": modelfile_content,
            }
            self.log.debug(
                f"'{self.uuid}' Start created model to ollama. payload: {payload}"
            )
            response = ResponseFormat(
                status=200,
                message=ResponseMessage(
                    action="Start to call model server",
                    task_uuid=str(self.uuid),
                    progress=progress_ratio * 0.5 + progress_base,
                    details={
                        "model": model,
                        "model_name_on_ollama": model_name_on_ollama,
                    },
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")

            # Make the POST request
            async with httpx.AsyncClient(follow_redirects=True) as client:
                try:
                    async with client.stream("POST", url, json=payload) as response:
                        async for line in response.aiter_lines():
                            if line.strip():
                                try:
                                    parsed_response = json.loads(line)
                                    self.log.debug(
                                        f"'{self.uuid}' Model server response:\n {parsed_response}\n"
                                    )
                                    # {"status":"using existing layer sha256:9845de86d85acee501671b2fa12bfb8c98adc36c82897eed479fbfb81ea6bedf"}
                                    # await self.message.put(
                                    #     json.dumps(
                                    #         {
                                    #             "status": 200,
                                    #             "message": f"Get model process status from ollama. status : {str(parsed_response['status'])}",
                                    #             "details": str(line),
                                    #         }
                                    #     )
                                    #     + "\n"
                                    # )

                                    #
                                    # print(parsed_response)
                                except json.JSONDecodeError as e:
                                    raise
                                    self.log.error(
                                        f"'{self.uuid}' Create model Get response error .Details: JSON decode error . {e}"
                                    )

                                    self.error_handler.add(
                                        type=self.error_handler.ERR_INTERNAL,
                                        loc=[self.error_handler.ERR_INTERNAL],
                                        msg=str(
                                            f"'{self.uuid}' Create model Get response error .Details: JSON decode error . {e}"
                                        ),
                                        input=dict(),
                                    )

                                    response = ResponseFormat(
                                        status=400,
                                        message=ResponseMessage(
                                            action="Model server processing failed.",
                                            task_uuid=str(self.uuid),
                                            progress=-1,
                                            details=dict(self.error_handler.errors),
                                        ),
                                    )
                                    await self.message.put(
                                        json.dumps(dict(response)) + "\n"
                                    )
                                    return
                except httpx.RequestError as e:
                    raise
                    self.log.error(
                        f"'{self.uuid}' Create model Request error.details: {e}"
                    )

                    self.error_handler.add(
                        type=self.error_handler.ERR_INTERNAL,
                        loc=[self.error_handler.ERR_INTERNAL],
                        msg=f"'{self.uuid}' Create model Request error.details: {e}",
                        input=dict(),
                    )

                    response = ResponseFormat(
                        status=400,
                        message=ResponseMessage(
                            action="Failed to call model server",
                            task_uuid=str(self.uuid),
                            progress=-1,
                            details=dict(self.error_handler.errors),
                        ),
                    )
                    await self.message.put(json.dumps(dict(response)) + "\n")
                    return
            response = ResponseFormat(
                status=200,
                message=ResponseMessage(
                    action="Success create model",
                    task_uuid=str(self.uuid),
                    progress=progress_ratio * 1 + progress_base,
                    details={
                        "model": model,
                        "model_name_on_ollama": model_name_on_ollama,
                    },
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")

            self.log.debug(f"'{self.uuid}' Success create model")

        except Exception as e:
            self.log.error(
                f"'{self.uuid}' Unexpected failed to create model. Details: {e}"
            )

            self.error_handler.add(
                type=self.error_handler.ERR_INTERNAL,
                loc=[self.error_handler.ERR_INTERNAL],
                msg=str(
                    f"'{self.uuid}' Unexpected failed to create model. Details: {e}"
                ),
                input=dict(),
            )

            response = ResponseFormat(
                status=500,
                message=ResponseMessage(
                    action="Unexpected failed to create model.",
                    task_uuid=str(self.uuid),
                    progress=-1,
                    details=dict(self.error_handler.errors[0]),
                ),
            )
            await self.message.put(json.dumps(dict(response)) + "\n")

        finally:
            self.alive = False
            del self.model_status[model]

    async def deploy(self, filename: str, model_name_on_ollama: str, file: UploadFile):
        model = filename.replace(".zip", "")
        if await self.save_model(model=filename, file=file, progress_ratio=0.5):
            self.alive = True
            await self.create_model(
                model=model,
                model_name_on_ollama=model_name_on_ollama,
                progress_ratio=0.5,
                progress_base=0.5,
            )
