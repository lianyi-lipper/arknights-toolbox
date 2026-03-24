import httpx

from skland.api import ZonaiApiClient
from skland.api import AuthCredInfo, ZonaiAuthApi, AccountAuthApi
from skland.model.exception import SklandApiException


class AccountAuthApiImpl(AccountAuthApi):
    """
    鹰角网络通行证基础鉴权接口实现类。
    实现具体的 HTTP 通信，访问 as.hypergryph.com 进行登录和授权过程。
    """
    def token_by_phone_password(self, phone: str, password: str) -> str:
        """
        调用官方接口，通过手机号和密码获取通行证 Token。
        如果返回状态码不为 0，会抛出 SklandApiException 异常。
        """
        resp = httpx.post(
            "https://as.hypergryph.com/user/auth/v1/token_by_phone_password",
            json={"phone": phone, "password": password}
        ).json()
        if resp["status"] != 0:
            raise SklandApiException(resp["status"], resp["msg"])
        return resp["data"]["token"]

    def grant_code(self, token: str, token_type: int = 0) -> str:
        """
        使用通行证 Token，向 oauth 服务申请 grant code。
        获取的授权码主要用于进一步交换森空岛的 Credential。
        """
        resp = httpx.post(
            "https://as.hypergryph.com/user/oauth2/v2/grant",
            json={
                "token": token,
                "appCode": "4ca99fa6b56cc2ba",  # oauth app code
                "type": token_type
            }
        ).json()
        if resp["status"] != 0:
            raise SklandApiException(resp["status"], resp["msg"])
        return resp["data"]["code"]


class ZonaiAuthApiImpl(ZonaiAuthApi):
    """
    森空岛授权鉴权接口实现类。
    实现具体的 HTTP 通信，使用获取的 code 去向森空岛服务换取核心鉴权信息（cred 等）。
    """
    def __init__(self, client: ZonaiApiClient):
        self.client = client

    def generate_cred_by_code(self, code: str) -> AuthCredInfo:
        """
        向森空岛服务发请求，使用通行证授权提取出的 code 换取 cred。
        返回封装的 AuthCredInfo 实例供客户端持久化或进一步请求。
        """
        resp = self.client.post(
            "/api/v1/user/auth/generate_cred_by_code",
            data={
                "code": code,
                "kind": 1
            }
        )
        return AuthCredInfo(cred=resp.data["cred"], user_id=resp.data["userId"], token=resp.data["token"])
