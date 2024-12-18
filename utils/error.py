import json
from dataclasses import dataclass
from typing import Literal, Union

from pydantic import BaseModel, model_validator


class ResponseErrorSchema(BaseModel):
    type: Union[str, None]
    loc: Union[list, None]
    msg: Union[str, None]
    input: Union[dict, None]

    @model_validator(mode="after")
    def normalize(self):
        self.msg = self.msg.title()
        return self


class ResponseErrorSchemaList(BaseModel):
    errors: list[ResponseErrorSchema]


@dataclass
class ResponseErrorType:
    ERR_VALIDATE: Literal["validate_error"] = "validate_error"
    ERR_POSTGRE: Literal["postgre_error"] = "postgre_error"
    ERR_REDIS: Literal["redis_error"] = "redis_error"
    ERR_INTERNAL: Literal["internal_error"] = "internal_error"
    ERR_UNEXPECTED: Literal["unexpected_error"] = "unexpected_error"


@dataclass
class ResponseErrorLoc:
    LOC_REQUEST: Literal["request"] = "request"
    LOC_BODY: Literal["body"] = "body"
    LOC_FORM: Literal["form"] = "form"
    LOC_QUERY: Literal["query"] = "query"
    LOC_DATABASE: Literal["database"] = "database"
    LOC_UNEXPECTED: Literal["unexpected"] = "unexpected"


class ResponseErrorHandler(ResponseErrorType, ResponseErrorLoc):
    def __init__(self) -> None:
        self._errors = []

    def add(self, type: str, loc: list, msg: str, input: dict):
        self._errors.append(
            ResponseErrorSchema(type=type, loc=loc, msg=msg, input=input).model_dump()
        )

    @property
    def errors(self) -> ResponseErrorSchemaList:
        return ResponseErrorSchemaList(errors=self._errors).model_dump()["errors"]


if __name__ == "__main__":
    reh = ResponseErrorHandler()
    reh.add(
        type=reh.ERR_REDIS, loc=[reh.LOC_DATABASE], msg="test", input={"aaa": "aaa"}
    )
    reh.add(
        type=reh.ERR_REDIS, loc=[reh.LOC_DATABASE], msg="test", input={"bbb": "bbb"}
    )
    print(json.dumps(reh.errors))
