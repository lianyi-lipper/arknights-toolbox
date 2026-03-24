from typing import Optional

from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class ZonaiResponse():
    """
    森空岛 API 基础响应数据结构。
    无论什么请求，往往都包裹在这层结构中返回。
    """
    code: int               # 错误码，0 表示成功
    message: str            # 提示信息 / 报错信息
    data: Optional[dict] = None  # 实际的有效载荷数据


class ZonaiApiClient:
    """
    森空岛底层 API 客户端抽象基类。
    定义了基础的网络请求方法以及凭证注入入口。
    """
    def set_credential(self, cred: str):
        """
        设置森空岛的核心访问凭证 cred。
        """
        raise NotImplementedError()

    def get(self, path, headers=None) -> ZonaiResponse:
        """
        发起 GET 请求抽象方法。
        """
        raise NotImplementedError()

    def post(self, path, data=None, headers=None) -> ZonaiResponse:
        """
        发起 POST 请求抽象方法。
        """
        raise NotImplementedError()

    def put(self, path, data=None, headers=None) -> ZonaiResponse:
        """
        发起 PUT 请求抽象方法。
        """
        raise NotImplementedError()

    def delete(self, path, data=None, headers=None) -> ZonaiResponse:
        """
        发起 DELETE 请求抽象方法。
        """
        raise NotImplementedError()
