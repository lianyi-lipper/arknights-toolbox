import json
from typing import Union

class SklandException(Exception):
    """
    Skland API 基础异常类。
    所有森空岛相关的自定义异常都应继承自该类。
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)

class SklandApiException(SklandException):
    """
    Skland API 请求异常类。
    当 API 返回的 code 不为 0 时抛出，包含具体的错误码和错误信息。
    """
    def __init__(self, code: int, message: str):
        """
        初始化 API 异常实例。

        :param code: API 返回的错误状态码
        :param message: API 返回的错误提示信息
        """
        self.code = code
        self.message = message

    def __str__(self):
        return f"SklandApiException {self.code}: {self.message}"
