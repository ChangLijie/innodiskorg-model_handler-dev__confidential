import json
import os
from string import Template
from typing import Callable

import httpx
from schema import GetModelList
from tools.connect import get_model_server_url, get_models_folder
from utils import config_logger, get_uuid, manager

from .zip_handler import ZipOperator

MODEL_CONFIG = config_logger("model.log", "w", "info")


class ModelOperator:
    def __init__(self):
        self.uuid = get_uuid()
        manager.create_room(self.uuid)
        self.root_path = get_models_folder()

    async def get_model_list(self, ws_sender: Callable[str, dict]):
        try:
            total_model_dir = next(os.walk(self.root_path))[1]
            content = GetModelList(
                **dict(total_nums=len(total_model_dir), model_list=total_model_dir)
            )
            MODEL_CONFIG.info(f"Get model list : {content.model_dump()}")
            await ws_sender(
                uuid=self.uuid,
                message={
                    "status": "success",
                    "message": content.model_dump(),
                },
            )

        except Exception as e:
            MODEL_CONFIG.error(f"Failed Get model list. details: {e}")
            await ws_sender(
                uuid=self.uuid,
                message={
                    "status": "error",
                    "message": "Model save error.",
                    "details": str(e),
                },
            )
        finally:
            await ws_sender(
                uuid=self.uuid,
                message={"end": True},
            )

    async def save_model(
        self, filename: str, file: bytes, ws_sender: Callable[str, dict]
    ):
        try:
            operator = ZipOperator(filename=filename)
            operator.save_zip(file=file)
            MODEL_CONFIG.info(f"Save '{filename}' success.")
            await ws_sender(
                uuid=self.uuid,
                message={
                    "status": "success",
                    "message": "Model save successfully.",
                },
            )

            operator.extract()
            MODEL_CONFIG.info(f"Upload '{filename}' success.")
            await ws_sender(
                uuid=self.uuid,
                message={
                    "status": "success",
                    "message": "Model extracted successfully.",
                },
            )

        except Exception as e:
            MODEL_CONFIG.error(f"Failed save model. details: {e}")
            await ws_sender(
                uuid=self.uuid,
                message={
                    "status": "error",
                    "message": "Model save error.",
                    "details": str(e),
                },
            )
        finally:
            await ws_sender(
                uuid=self.uuid,
                message={"end": True},
            )

    async def create_model(
        self, model: str, model_name_on_ollama: str, ws_sender: Callable[str, dict]
    ):
        try:
            model_server_url = get_model_server_url()
            url = model_server_url + "api/create"
            model_folder = os.path.join(self.root_path, model)
            ollama_model_folder = os.path.join(
                "/home", model
            )  # Check if the model folder exists

            if not os.path.exists(model_folder):
                await ws_sender(
                    uuid=self.uuid,
                    message={"status": "error", "message": "Model not exist."},
                )
                MODEL_CONFIG.warning(f"{model} not exist.")
                raise FileExistsError(f"{model} not exist.")
            files = next(os.walk(model_folder))[2]
            modelfile_content = ""
            basemodel_template = Template("FROM $base_model_path")
            gguf_template = Template("\nADAPTER $gguf_path")

            # Prepare the modelfile content
            if len(files) == 0:
                if "lora" in files[0]:
                    base_model_path = os.path.join(ollama_model_folder, files[1])
                    gguf_path = os.path.join(ollama_model_folder, files[0])
                else:
                    base_model_path = os.path.join(ollama_model_folder, files[0])
                    gguf_path = os.path.join(ollama_model_folder, files[1])

                modelfile_content = basemodel_template.substitute(
                    base_model_path=base_model_path
                ) + gguf_template.substitute(gguf_path=gguf_path)
            else:
                base_model_path = os.path.join(ollama_model_folder, files[0])
                modelfile_content = basemodel_template.substitute(
                    base_model_path=base_model_path
                )

            # Prepare payload
            payload = {
                "model": model_name_on_ollama,
                "modelfile": modelfile_content,
            }
            MODEL_CONFIG.debug(f"Start created model to ollama. payload: {payload}")
            # Make the POST request
            async with httpx.AsyncClient(follow_redirects=True) as client:
                try:
                    async with client.stream("POST", url, json=payload) as response:
                        async for line in response.aiter_lines():
                            if line.strip():
                                try:
                                    # parsed_response = json.loads(line)

                                    await ws_sender(
                                        uuid=self.uuid,
                                        message={
                                            "status": "success",
                                            "message": "Get model process status from ollama.",
                                            "details": str(line),
                                        },
                                    )
                                    # print(parsed_response)
                                except json.JSONDecodeError as e:
                                    MODEL_CONFIG.error(
                                        f"JSON decode error.details: {e}"
                                    )
                                    await ws_sender(
                                        uuid=self.uuid,
                                        message={
                                            "status": "error",
                                            "message": "JSON decode error",
                                            "details": f"{e}, line: {line}",
                                        },
                                    )
                except httpx.RequestError as e:
                    MODEL_CONFIG.error(f"Request error.details: {e}")
                    await ws_sender(
                        uuid=self.uuid,
                        message={
                            "status": "error",
                            "message": "Request error",
                            "details": str(e),
                        },
                    )
        except Exception as e:
            MODEL_CONFIG.error(f"Unexpected failed to create model..details: {e}")
            await ws_sender(
                uuid=self.uuid,
                message={
                    "status": "error",
                    "message": "Unexpected failed to create model.",
                    "details": str(e),
                },
            )
        finally:
            await ws_sender(
                uuid=self.uuid,
                message={"end": True},
            )
