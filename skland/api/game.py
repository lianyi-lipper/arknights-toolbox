from typing import List

from dataclasses_json import dataclass_json, LetterCase
from dataclasses import dataclass

from skland.model.player import PlayerInfo
from skland.model.attendance import AttendanceInfo


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AppBinding:
    """
    单个游戏角色绑定记录。
    代表用户在某一渠道或服务器下绑定的特定角色（如明日方舟某官服角色）。
    """
    uid: str                 # 游戏内角色 UID
    channel_master_id: str   # 渠道主 ID（如 1 代表官服，2 代表 B 服等）
    is_delete: bool          # 是否已删除
    channel_name: str        # 渠道名称（如 "官服", "Bilibili" 等）
    is_default: bool         # 是否为默认选择的角色
    is_official: bool        # 是否为官方渠道
    nick_name: str           # 游戏内玩家昵称


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AppBindingContainer:
    """
    游戏绑定聚合容器。
    代表一款游戏（如明日方舟）下的所有绑定角色信息聚合。
    """
    binding_list: List[AppBinding]  # 绑定的角色列表
    default_uid: str = ""           # 默认角色 UID
    app_name: str = ""              # 游戏名称 (如 '明日方舟')
    app_code: str = ""              # 游戏代码 (如 'arknights')


class ZonaiGameApi:
    """
    森空岛游戏数据获取抽象类的基类。
    定义了获取玩家基础信息和角色绑定列表的约定。
    """
    def player_info(self, uid: str) -> PlayerInfo:
        """
        获取指定角色的玩家详情，返回结构化 PlayerInfo 对象（干员列表、理智、状态等）。
        :param uid: 游戏内角色 UID
        """
        raise NotImplementedError()

    def player_info_raw(self, uid: str) -> dict:
        """
        获取指定角色的玩家详情原始 dict，可访问全部字段（含 building/recruit 等未完全建模数据）。
        :param uid: 游戏内角色 UID
        """
        raise NotImplementedError()

    def player_binding(self) -> List[AppBindingContainer]:
        """
        获取当前登录账号的所有游戏角色绑定列表。
        返回封装好的 AppBindingContainer 对象列表。
        """
        raise NotImplementedError()

    def attendance(self, uid: str, game_id: str = "1") -> AttendanceInfo:
        """
        获取签到日历与奖励信息。
        :param uid: 游戏内角色 UID
        :param game_id: 游戏 ID，明日方舟默认为 '1'
        """
        raise NotImplementedError()
