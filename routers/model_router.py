import asyncio
import json
from typing import Optional

from fastapi import APIRouter, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from schema import CreateModel, UploadModel
from tools.model_handler import ModelOperator
from utils import ResponseErrorHandler, config_logger
from utils.background_excutor import TaskExecutor

router = APIRouter()


MODEL_CONFIG = config_logger("model_api.log", "w", "info")
task_executor = TaskExecutor(max_workers=10)


@router.get("/model", tags=["Get models list"])
async def get_models(
    # stream: bool = Query(default=True, description="Enable streaming response"),
):
    error_handler = ResponseErrorHandler()
    try:
        message = asyncio.Queue()
        operator = ModelOperator(message=message)
        task_executor.run_in_background(operator.get_model_list)
        MODEL_CONFIG.info(f"Start get model ({operator.uuid})")
        # if stream:
        return StreamingResponse(
            content=operator.get_status(),
            media_type="application/json",
        )

    except Exception as e:
        MODEL_CONFIG.error("Start get model list error {}".format(e))
        error_handler.add(
            type=error_handler.ERR_UNEXPECTED,
            loc=[error_handler.LOC_UNEXPECTED],
            msg=str(e),
            input=dict(),
        )
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps(error_handler.errors),
            media_type="application/json",
        )


@router.post("/upload", tags=["Upload data"])
async def upload(
    model: Optional[UploadFile],
):
    request_body = UploadModel(model=model)
    error_handler = ResponseErrorHandler()
    try:
        message = asyncio.Queue()
        operator = ModelOperator(message=message)
        filename = request_body.model.filename
        file = await request_body.model.read()

        task_executor.run_in_background(
            operator.save_model,
            filename=filename,
            file=file,
        )
        MODEL_CONFIG.info(
            f"Start upload model ({operator.uuid}): model : {filename.replace('.zip', '')}"
        )
        return StreamingResponse(
            content=operator.get_status(),
            media_type="application/json",
        )

    except Exception as e:
        MODEL_CONFIG.error("Start upload model error {}".format(e))
        error_handler.add(
            type=error_handler.ERR_UNEXPECTED,
            loc=[error_handler.LOC_UNEXPECTED],
            msg=str(e),
            input=dict(),
        )
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps(error_handler.errors),
            media_type="application/json",
        )


@router.post("/model/create", tags=["Create Model on Ollama"])
def create_model(
    request: CreateModel,
):
    error_handler = ResponseErrorHandler()
    try:
        message = asyncio.Queue()
        model = request.model

        model_name_on_ollama = request.model_name_on_ollama
        operator = ModelOperator(message=message)
        task_executor.run_in_background(
            operator.create_model,
            model=model,
            model_name_on_ollama=model_name_on_ollama,
        )

        MODEL_CONFIG.info(
            f"Start create model ({operator.uuid}): model : {model} , model name on ollama : {model_name_on_ollama}"
        )
        return StreamingResponse(
            content=operator.get_status(),
            media_type="application/json",
        )

    except Exception as e:
        MODEL_CONFIG.error("Start create model error {}".format(e))
        error_handler.add(
            type=error_handler.ERR_UNEXPECTED,
            loc=[error_handler.LOC_UNEXPECTED],
            msg=str(e),
            input=dict(),
        )
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps(error_handler.errors),
            media_type="application/json",
        )
