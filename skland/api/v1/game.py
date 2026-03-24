from typing import List

from skland.api import ZonaiGameApi, ZonaiApiClient, AppBindingContainer
from skland.model.player import PlayerInfo
from skland.model.attendance import AttendanceInfo


class ZonaiGameApiImpl(ZonaiGameApi):
    """
    森空岛游戏数据接口实现类 (V1 API)。
    通过已验证的客户端获取玩家相关的游戏绑定状态与详细信息。
    """
    def __init__(self, client: ZonaiApiClient):
        self.client = client

    def player_info(self, uid: str) -> PlayerInfo:
        """
        获取指定玩家 UID 的详细信息，返回结构化 PlayerInfo。
        包含玩家状态、干员列表、助战干员等数据。
        """
        data = self.client.get(f"/api/v1/game/player/info?uid={uid}").data
        return PlayerInfo.from_dict(data)

    def player_info_raw(self, uid: str) -> dict:
        """
        获取玩家详情原始 dict，可访问全部字段（含 building/recruit 等）。
        """
        return self.client.get(f"/api/v1/game/player/info?uid={uid}").data

    def player_binding(self) -> List[AppBindingContainer]:
        """
        获取当前已登录用户的应用（游戏）角色绑定列表。
        返回 AppBindingContainer 实例列表，每一个实例对应一个被绑定的游戏账号角色信息（如《明日方舟》角色名、服务器 ID 等）。
        """
        return [AppBindingContainer.from_dict(item) for item in self.client.get(
            "/api/v1/game/player/binding?"
        ).data["list"]]

    def attendance(self, uid: str, game_id: str = "1") -> AttendanceInfo:
        """
        获取签到日历，包含本月奖励列表和签到状态。
        """
        data = self.client.get(
            f"/api/v1/game/attendance?uid={uid}&gameId={game_id}"
        ).data
        return AttendanceInfo.from_dict(data)
