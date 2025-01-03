import asyncio
import json
import os
import shutil
from string import Template

import httpx
from tools.connect import get_model_server_url, get_models_folder
from utils import ResponseErrorHandler, config_logger, get_uuid

from .zip_handler import ZipOperator

MODEL_STATUS = {}


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
            await self.message.put(
                (
                    json.dumps(
                        {"status": 200, "message": f"Start Delete Model {model}"}
                    )
                    + "\n"
                )
            )
            shutil.rmtree(model_path)
            await self.message.put(
                (
                    json.dumps(
                        {
                            "status": 200,
                            "message": f"Delete Model {model} success.",
                        }
                    )
                    + "\n"
                )
            )
            self.log.warning(f"'{self.uuid}'Delete model success.Details : {model}.")

        except Exception as e:
            self.log.error(f"'{self.uuid}' Failed Delete model list. Details: {e}")
            self.error_handler.add(
                type=self.error_handler.ERR_INTERNAL,
                loc=[self.error_handler.ERR_INTERNAL],
                msg=str(f"'{self.uuid}' Failed Delete model list. Details: {e}"),
                input=dict(),
            )
            error = {
                "status": 500,
                "message": json.dumps(self.error_handler.errors) + "\n",
            }
            await self.message.put(error)
            await asyncio.sleep(0.1)
        finally:
            await asyncio.sleep(0.1)
            del self.model_status[model]
            self.alive = False
            # await self.message.put(
            #     json.dumps({"status": 200, "message": {"end": True}})
            # )

    async def get_status(self):
        while self.alive or not self.message.empty():
            if not self.message.empty():
                raw_message = await self.message.get()
                try:
                    # 檢查 raw_message 的類型，避免多次解析
                    if isinstance(raw_message, str):
                        message = json.loads(raw_message)
                    elif isinstance(raw_message, dict):
                        message = raw_message
                    else:
                        raise TypeError(
                            f"Unsupported message type: {type(raw_message)}"
                        )

                    yield message["status"], message["message"]
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    self.log.error(
                        f"Failed to process message: {raw_message}, Error: {e}"
                    )
                    yield 500, {"error": "Invalid message format"}
            await asyncio.sleep(0.1)

    async def get_model_list(self):
        try:
            total_model_dir = next(os.walk(self.root_path))[1]

            self.log.info(f"'{self.uuid}'Get model list. Detail:{total_model_dir}")

            for model in total_model_dir:
                await self.message.put(
                    (json.dumps({"status": 200, "message": {"model": model}}) + "\n")
                )
                await asyncio.sleep(0.1)

        except Exception as e:
            self.log.error(f"'{self.uuid}' Failed Get model list. Details: {e}")
            self.error_handler.add(
                type=self.error_handler.ERR_INTERNAL,
                loc=[self.error_handler.ERR_INTERNAL],
                msg=str(f"'{self.uuid}' Failed Get model list. Details: {e}"),
                input=dict(),
            )
            error = {
                "status": 500,
                "message": json.dumps(self.error_handler.errors) + "\n",
            }
            await self.message.put(error)
            await asyncio.sleep(0.1)
        finally:
            await asyncio.sleep(0.1)
            self.alive = False
            # await self.message.put(
            #     json.dumps({"status": 200, "message": {"end": True}})
            # )

    async def save_model(self, model: str, file: bytes):
        try:
            self.model_status[model] = self.uuid
            operator = ZipOperator(filename=model)
            operator.save_zip(file=file)
            self.log.info(f"'{self.uuid}' Save '{model}' success.")

            await self.message.put(
                json.dumps(
                    {
                        "status": 200,
                        "message": f"Save '{model}' success.",
                    }
                )
                + "\n"
            )

            await asyncio.sleep(0.1)

            operator.extract()
            self.log.info(f"'{self.uuid}' Upload '{model}' success.")
            await self.message.put(
                json.dumps(
                    {
                        "status": 200,
                        "message": "Model extracted successfully.",
                    }
                )
                + "\n"
            )
            await asyncio.sleep(0.1)
        except Exception as e:
            self.log.error(f"'{self.uuid}' Failed save model. Details: {e}")
            self.error_handler.add(
                type=self.error_handler.ERR_INTERNAL,
                loc=[self.error_handler.ERR_INTERNAL],
                msg=str(f"'{self.uuid}' Failed save model. Details: {e}"),
                input=dict(),
            )

            error = {
                "status": 500,
                "message": json.dumps(self.error_handler.errors) + "\n",
            }
            await self.message.put(error)
            await asyncio.sleep(0.1)
        finally:
            await asyncio.sleep(0.1)
            self.alive = False
            del self.model_status[model]
            # await self.message.put(
            #     json.dumps({"status": 200, "message": {"end": True}})
            # )

    async def create_model(self, model: str, model_name_on_ollama: str):
        try:
            self.model_status[model] = self.uuid
            model_server_url = get_model_server_url()
            url = model_server_url + "api/create"
            model_folder = os.path.join(self.root_path, model)
            ollama_model_folder = os.path.join(
                "/home", model
            )  # Check if the model folder exists

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

                error = {
                    "status": 500,
                    "message": json.dumps(self.error_handler.errors) + "\n",
                }
                await self.message.put(error)
                await asyncio.sleep(0.1)

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
                error = {
                    "status": 500,
                    "message": json.dumps(self.error_handler.errors) + "\n",
                }
                await self.message.put(error)
                await asyncio.sleep(0.1)
            # Prepare payload
            payload = {
                "model": model_name_on_ollama,
                "modelfile": modelfile_content,
            }
            self.log.debug(
                f"'{self.uuid}' Start created model to ollama. payload: {payload}"
            )
            # Make the POST request
            async with httpx.AsyncClient(follow_redirects=True) as client:
                try:
                    async with client.stream("POST", url, json=payload) as response:
                        async for line in response.aiter_lines():
                            if line.strip():
                                try:
                                    # parsed_response = json.loads(line)

                                    await self.message.put(
                                        json.dumps(
                                            {
                                                "status": 200,
                                                "message": f"Get model process status from ollama. details : {str(line)}",
                                                "details": str(line),
                                            }
                                        )
                                        + "\n"
                                    )

                                    await asyncio.sleep(0.1)
                                    # print(parsed_response)
                                except json.JSONDecodeError as e:
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

                                    error = {
                                        "status": 400,
                                        "message": json.dumps(self.error_handler.errors)
                                        + "\n",
                                    }
                                    await self.message.put(error)
                                    await asyncio.sleep(0.1)
                except httpx.RequestError as e:
                    self.log.error(
                        f"'{self.uuid}' Create model Request error.details: {e}"
                    )

                    self.error_handler.add(
                        type=self.error_handler.ERR_INTERNAL,
                        loc=[self.error_handler.ERR_INTERNAL],
                        msg=f"'{self.uuid}' Create model Request error.details: {e}",
                        input=dict(),
                    )

                    error = {
                        "status": 400,
                        "message": json.dumps(self.error_handler.errors) + "\n",
                    }
                    await self.message.put(error)
                    await asyncio.sleep(0.1)

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

            error = {
                "status": 500,
                "message": json.dumps(self.error_handler.errors) + "\n",
            }
            await self.message.put(error)
            await asyncio.sleep(0.1)
        finally:
            await asyncio.sleep(0.1)
            self.alive = False
            del self.model_status[model]
            # await self.message.put(
            #     json.dumps({"status": 200, "message": {"end": True}})
            # )
