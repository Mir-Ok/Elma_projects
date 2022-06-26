from functools import wraps
from typing import Callable, Tuple, Optional, Union, Iterable, Type

from flask import request, make_response, Response
from flask_pydantic.core import unsupported_media_type_response
from flask_pydantic.exceptions import JsonBodyParsingError
from pydantic import ValidationError, BaseModel, parse_obj_as

from settings import logger
from validate_request.models import ResponseModel


def validate_path_params(func: Callable, kwargs: dict) -> Tuple[dict, list]:
    errors = []
    validated = {}
    for name, type_ in func.__annotations__.items():  # noqa
        if name in {"query", "body", "return"}:
            continue
        try:
            value = parse_obj_as(type_, kwargs.get(name))
            validated[name] = value
        except ValidationError as e:
            err = e.errors()[0]
            err["loc"] = [name]  # noqa
            errors.append(err)
    kwargs = {**kwargs, **validated}
    return kwargs, errors


def get_body_dict(**params):
    data = request.get_json(**params)
    logger.info(f"path: {request.path}")
    logger.info(f"headers: {request.headers}")
    logger.info(f"body: {data}")
    if data is None and params.get("silent"):
        return {}
    return data


def make_json_response(
        content: Union[BaseModel, Iterable[BaseModel]],
        status_code: int,
        by_alias: bool = True,
        exclude_none: bool = False,
        many: bool = False,
) -> Response:
    """serializes model, creates JSON response with given status code"""
    if many:
        json_data = [
            model.json(exclude_none=exclude_none, by_alias=by_alias)
            for model in content
        ]
        js = f"[{', '.join(json_data)}]"
    else:
        js = content.json(exclude_none=exclude_none, by_alias=by_alias)
    logger.warning(f"Response result: {js}")
    response = make_response(js, status_code)
    response.mimetype = "application/json"
    return response


def validate(
        body: Optional[Type[BaseModel]] = None,
        response: Optional[Type[BaseModel]] = None,
        on_success_status: int = 200,
        by_alias: bool = True,
        get_json_params: Optional[dict] = None
):
    """Валидация входящего запроса."""
    def decorate(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            b, error = None, {}
            kwargs, path_err = validate_path_params(func, kwargs)
            if path_err:
                error["path_params"] = path_err

            body_in_kwargs = func.__annotations__.get("body")  # noqa: F401
            body_model = body_in_kwargs or body

            response_in_kwargs = func.__annotations__.get("response")  # noqa: F401
            response_model = response_in_kwargs or response or ResponseModel

            if body_model:
                body_params = get_body_dict(**(get_json_params or {}))
                if "__root__" in body_model.__fields__:
                    try:
                        b = body_model(__root__=body_params).__root__
                    except ValidationError as err:
                        error["body_params"] = err.errors()
                else:
                    try:
                        b = body_model(**body_params)
                    except TypeError:
                        content_type = request.headers.get("Content-Type",
                                                           "").lower()
                        media_type = content_type.split(";")[0]
                        if media_type != "application/json":
                            return unsupported_media_type_response(
                                content_type)
                        else:
                            raise JsonBodyParsingError()
                    except ValidationError as err:
                        error["body_params"] = err.errors()
            request.body_params = b
            if body_in_kwargs:
                kwargs["body"] = b

            if error:
                logger.error(error)
                status_code = 400
                content = response_model(error=[error])
                r = make_json_response(content, status_code, by_alias)
                return r

            res = func(*args, **kwargs)

            if isinstance(res, BaseModel):
                return make_json_response(
                    res,
                    on_success_status,
                    by_alias,
                )

            if (
                    isinstance(res, tuple)
                    and len(res) == 2
                    and isinstance(res[0], BaseModel)
            ):
                return make_json_response(
                    res[0],
                    res[1],
                    by_alias,
                )

            return res
        return wrapper
    return decorate
