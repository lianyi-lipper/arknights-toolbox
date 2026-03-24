from dataclasses import dataclass


class AccountAuthApi:
    """
    鹰角网络通行证基础鉴权接口。
    用于通过账号密码获取 token，以及通过 token 获取授权 code。
    """
    def token_by_phone_password(self,phone: str, password: str) -> str:
        """
        通过手机号和密码获取通行证 token。
        :param phone: 手机号码
        :param password: 密码
        :return: 获取到的 token 字符串
        """
        raise NotImplementedError()

    def grant_code(self, token: str, token_type: int) -> str:
        """
        通过通行证 token 获取授权 code，用于后续换取森空岛 credential。
        :param token: 通行证 token
        :param token_type: token 类型 (通常为 1)
        :return: 授权 code 字符串
        """
        raise NotImplementedError()


@dataclass
class AuthCredInfo:
    """
    授权凭证信息数据类，用于保存登录成功后的关键认证数据。
    """
    cred: str        # 森空岛核心凭证 cred
    user_id: str     # 用户 ID
    token: str = ""  # 登录返回的高级凭证 token


class ZonaiAuthApi:
    """
    森空岛鉴权接口。
    用于通过授权 code 生成森空岛凭证 cred。
    """
    def generate_cred_by_code(self, code: str) -> AuthCredInfo:
        """
        使用鹰角网络通行证授权获取的 code 生成森空岛凭证。
        :param code: 授权 code
        :return: 包含 cred 等信息的 AuthCredInfo 实例
        """
        raise NotImplementedError()
