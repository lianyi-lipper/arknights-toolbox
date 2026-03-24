from skland.api.auth import *
from skland.api.client import *
from skland.api.game import *


class SklandApi:
    """
    森空岛核心 API 抽象门面基类。
    组织了各类鉴权和游戏业务的 API 定义，子类将实现这些具体功能分支的挂载点。
    """
    def __init__(self):
        self.account = AccountAuthApi()
        self.auth = ZonaiAuthApi()
        self.game = ZonaiGameApi()

    def init(self, cred: str, sign_token: str = ""):
        """
        根据 cred（及可选的 sign_token）快速初始化客户端。
        """
        raise NotImplementedError()
