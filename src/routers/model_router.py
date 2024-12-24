import json
from typing import Optional

from fastapi import APIRouter, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from schema import CreateModel, DeleteModel, UploadModel
from tools.model_handler import MODEL_STATUS, ModelOperator
from utils import ResponseErrorHandler, config_logger
from utils.background_excutor import TaskExecutor

router = APIRouter()


TASK_LOG = config_logger(
    file_name="system.log",
    write_mode="w",
    level="info",
    logger_name="model_router_logger",
)
task_executor = TaskExecutor(max_workers=10)


@router.get("/model", tags=["Get models list"])
async def get_models(
    # stream: bool = Query(default=True, description="Enable streaming response"),
):
    error_handler = ResponseErrorHandler()
    try:
        operator = ModelOperator()
        task_executor.run_in_background(task=operator.get_model_list)
        TASK_LOG.info(f"Start get model ({operator.uuid})")

        async def event_generator():
            async for status_code, message in operator.get_status():
                yield json.dumps({"status": status_code, "message": message}) + "\n"

        return StreamingResponse(
            content=event_generator(),
            media_type="application/json",
        )

    except Exception as e:
        TASK_LOG.error(f"'{operator.uuid}'Get model list error. Details : {e}")
        error_handler.add(
            type=error_handler.ERR_UNEXPECTED,
            loc=[error_handler.LOC_UNEXPECTED],
            msg=f"'{operator.uuid}'Get model list error. Details : {e}",
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
        operator = ModelOperator()
        filename = request_body.model.filename
        file = await request_body.model.read()

        task_executor.run_in_background(
            operator.save_model,
            model=filename,
            file=file,
        )

        TASK_LOG.info(
            f"Start upload model ({operator.uuid}): model : {filename.replace('.zip', '')}"
        )

        async def event_generator():
            async for status_code, message in operator.get_status():
                yield json.dumps({"status": status_code, "message": message}) + "\n"

        return StreamingResponse(
            content=event_generator(),
            media_type="application/json",
        )

    except Exception as e:
        TASK_LOG.error(f"'{operator.uuid}' Upload model error. Details :{e}")
        error_handler.add(
            type=error_handler.ERR_UNEXPECTED,
            loc=[error_handler.LOC_UNEXPECTED],
            msg=f"'{operator.uuid}' Upload model error. Details :{e}",
            input=dict(),
        )
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps(error_handler.errors),
            media_type="application/json",
        )


@router.delete("/model", tags=["Delete Innodisk Model."])
def delete_model(
    request: DeleteModel,
):
    error_handler = ResponseErrorHandler()
    try:
        model = request.model
        operator = ModelOperator()
        if model in MODEL_STATUS:
            error_handler.add(
                type=error_handler.ERR_INTERNAL,
                loc=[error_handler.ERR_INTERNAL],
                msg=f"Model '{model}' is currently in use and cannot be deleted.",
                input={},
            )
            TASK_LOG.info(
                f"Failed Delete model ({operator.uuid}): model : {model} is currently in use and cannot be deleted."
            )
            return Response(
                status_code=status.HTTP_403_FORBIDDEN,
                content=json.dumps(error_handler.errors),
                media_type="application/json",
            )

        task_executor.run_in_background(
            operator.delete_model,
            model=model,
        )

        TASK_LOG.info(f"Start Delete model ({operator.uuid}): model : {model}.")

        async def event_generator():
            async for status_code, message in operator.get_status():
                yield json.dumps({"status": status_code, "message": message}) + "\n"

        return StreamingResponse(
            content=event_generator(),
            media_type="application/json",
        )

    except Exception as e:
        TASK_LOG.error(f"'{operator.uuid}' Delete model error. Details : {e}")
        error_handler.add(
            type=error_handler.ERR_UNEXPECTED,
            loc=[error_handler.LOC_UNEXPECTED],
            msg=f"'{operator.uuid}' Delete model error. Details : {e}",
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
        model = request.model

        model_name_on_ollama = request.model_name_on_ollama
        operator = ModelOperator()
        task_executor.run_in_background(
            operator.create_model,
            model=model,
            model_name_on_ollama=model_name_on_ollama,
        )

        TASK_LOG.info(
            f"Start create model ({operator.uuid}): model : {model} , model name on ollama : {model_name_on_ollama}"
        )

        async def event_generator():
            async for status_code, message in operator.get_status():
                yield json.dumps({"status": status_code, "message": message}) + "\n"

        return StreamingResponse(
            content=event_generator(),
            media_type="application/json",
        )

    except Exception as e:
        TASK_LOG.error(f"'{operator.uuid}' Create model error. Details : {e}")
        error_handler.add(
            type=error_handler.ERR_UNEXPECTED,
            loc=[error_handler.LOC_UNEXPECTED],
            msg=f"'{operator.uuid}' Create model error. Details : {e}",
            input=dict(),
        )
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps(error_handler.errors),
            media_type="application/json",
        )
