from skland.api import SklandApi
from skland.api.v1.auth import ZonaiAuthApiImpl, AccountAuthApiImpl
from skland.api.v1.client import HttpxClient
from skland.api.v1.game import ZonaiGameApiImpl


class SklandApiV1(SklandApi):
    """
    森空岛 V1 版 API 聚合门面 (Facade)。
    组合了 HttpxClient (网络通信)、AccountAuthApiImpl (鹰角网络通行证)、ZonaiAuthApiImpl (森空岛鉴权) 和 ZonaiGameApiImpl (游戏数据)，对外提供一个干净的入口。
    """
    def __init__(self):
        super().__init__()
        self.client = HttpxClient("https://zonai.skland.com")
        self.account = AccountAuthApiImpl()
        self.auth = ZonaiAuthApiImpl(self.client)
        self.game = ZonaiGameApiImpl(self.client)

    def init(self, cred: str, sign_token: str = ""):
        """
        通过已有的凭证信息快速初始化客户端，跳过手机号密码登录环节。
        """
        self.client.set_credential(cred, sign_token)
