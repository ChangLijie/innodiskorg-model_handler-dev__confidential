import asyncio
import json
import os
from string import Template

import httpx
from tools.connect import get_model_server_url, get_models_folder
from utils import ResponseErrorHandler, config_logger, get_uuid, manager

from .zip_handler import ZipOperator

MODEL_CONFIG = config_logger("model.log", "w", "info")


class ModelOperator:
    def __init__(self, message: asyncio.Queue):
        self.uuid = get_uuid()
        manager.create_room(self.uuid)
        self.root_path = get_models_folder()
        self.message = message
        self.alive = True
        self.error_handler = ResponseErrorHandler()

    async def get_status(self):
        while self.alive or not self.message.empty():
            if not self.message.empty():
                message = await self.message.get()
                yield message
            await asyncio.sleep(0.1)

    async def get_model_list(self):
        try:
            total_model_dir = next(os.walk(self.root_path))[1]

            MODEL_CONFIG.info(f"Get model list : {total_model_dir}")

            for model in total_model_dir:
                await self.message.put(
                    (
                        json.dumps({"status": "success", "message": {"model": model}})
                        + "\n"
                    )
                )
                await asyncio.sleep(0.1)

        except Exception as e:
            MODEL_CONFIG.error(f"Failed Get model list. details: {e}")
            self.error_handler.add(
                type=self.error_handler.ERR_INTERNAL,
                loc=[self.error_handler.ERR_INTERNAL],
                msg=str(f"Failed Get model list. details: {e}"),
                input=dict(),
            )
            await self.message.put(json.dumps(self.error_handler.errors) + "\n")
            await asyncio.sleep(0.1)
        finally:
            await asyncio.sleep(0.1)
            self.alive = False
            await self.message.put(
                json.dumps({"status": "success", "message": {"end": True}})
            )

    async def save_model(self, filename: str, file: bytes):
        try:
            operator = ZipOperator(filename=filename)
            operator.save_zip(file=file)
            MODEL_CONFIG.info(f"Save '{filename}' success.")

            await self.message.put(
                json.dumps(
                    {
                        "status": "success",
                        "message": f"Save '{filename}' success.",
                    }
                )
                + "\n"
            )

            await asyncio.sleep(0.1)

            operator.extract()
            MODEL_CONFIG.info(f"Upload '{filename}' success.")
            await self.message.put(
                json.dumps(
                    {
                        "status": "success",
                        "message": "Model extracted successfully.",
                    }
                )
                + "\n"
            )
            await asyncio.sleep(0.1)
        except Exception as e:
            MODEL_CONFIG.error(f"Failed save model. details: {e}")
            self.error_handler.add(
                type=self.error_handler.ERR_INTERNAL,
                loc=[self.error_handler.ERR_INTERNAL],
                msg=str(f"Failed save model. details: {e}"),
                input=dict(),
            )

            await self.message.put(json.dumps(self.error_handler.errors) + "\n")
            await asyncio.sleep(0.1)
        finally:
            await asyncio.sleep(0.1)
            self.alive = False
            await self.message.put(
                json.dumps({"status": "success", "message": {"end": True}})
            )

    async def create_model(self, model: str, model_name_on_ollama: str):
        try:
            model_server_url = get_model_server_url()
            url = model_server_url + "api/create"
            model_folder = os.path.join(self.root_path, model)
            ollama_model_folder = os.path.join(
                "/home", model
            )  # Check if the model folder exists

            if not os.path.exists(model_folder):
                MODEL_CONFIG.warning(f"{model} not exist.")
                self.error_handler.add(
                    type=self.error_handler.ERR_INTERNAL,
                    loc=[self.error_handler.ERR_INTERNAL],
                    msg=str("Model not exist."),
                    input=dict(),
                )

                await self.message.put(json.dumps(self.error_handler.errors) + "\n")
                await asyncio.sleep(0.1)

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

                                    await self.message.put(
                                        json.dumps(
                                            {
                                                "status": "success",
                                                "message": "Get model process status from ollama.",
                                                "details": str(line),
                                            }
                                        )
                                        + "\n"
                                    )

                                    await asyncio.sleep(0.1)
                                    # print(parsed_response)
                                except json.JSONDecodeError as e:
                                    MODEL_CONFIG.error(
                                        f"JSON decode error.details: {e}"
                                    )

                                    self.error_handler.add(
                                        type=self.error_handler.ERR_INTERNAL,
                                        loc=[self.error_handler.ERR_INTERNAL],
                                        msg=str(f"JSON decode error.details: {e}"),
                                        input=dict(),
                                    )

                                    await self.message.put(
                                        json.dumps(self.error_handler.errors) + "\n"
                                    )
                                    await asyncio.sleep(0.1)
                except httpx.RequestError as e:
                    MODEL_CONFIG.error(f"Request error.details: {e}")

                    self.error_handler.add(
                        type=self.error_handler.ERR_INTERNAL,
                        loc=[self.error_handler.ERR_INTERNAL],
                        msg=str(f"Request error.details: {e}"),
                        input=dict(),
                    )

                    await self.message.put(json.dumps(self.error_handler.errors) + "\n")
                    await asyncio.sleep(0.1)

        except Exception as e:
            MODEL_CONFIG.error(f"Unexpected failed to create model..details: {e}")

            self.error_handler.add(
                type=self.error_handler.ERR_INTERNAL,
                loc=[self.error_handler.ERR_INTERNAL],
                msg=str(f"Unexpected failed to create model..details: {e}"),
                input=dict(),
            )

            await self.message.put(json.dumps(self.error_handler.errors) + "\n")
            await asyncio.sleep(0.1)
        finally:
            await asyncio.sleep(0.1)
            self.alive = False
            await self.message.put(
                json.dumps({"status": "success", "message": {"end": True}})
            )
