"""
明日方舟签到/出勤数据模型 (attendance 接口对应)

结构来源: /api/v1/game/attendance?uid=xxx&gameId=1 真实响应
"""
from dataclasses import dataclass, field
from typing import List
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AttendanceItem:
    """
    单个签到日奖励项。
    - resource_id: 奖励物品 ID（可在 resourceInfoMap 中查名称）
    - type: 'first'=首次奖励, 'daily'=每日
    - count: 数量
    - available: 当前是否可领取
    - done: 是否已领取
    """
    resource_id: str = ""
    type: str = ""
    count: int = 0
    available: bool = False
    done: bool = False


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AttendanceInfo:
    """
    /api/v1/game/attendance 响应结构。
    包含本月签到日历、历史签到记录、奖励物品信息字典。
    """
    current_ts: str = ""
    calendar: List[AttendanceItem] = field(default_factory=list)
    records: List[dict] = field(default_factory=list)
    resource_info_map: dict = field(default_factory=dict)

    @property
    def today_rewards(self) -> List[AttendanceItem]:
        """今日可领取的奖励列表"""
        return [item for item in self.calendar if item.available and not item.done]

    @property
    def is_signed_today(self) -> bool:
        """今天是否已签到"""
        return all(item.done for item in self.calendar if item.available)
