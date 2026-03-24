"""
明日方舟玩家数据模型 (player_info 接口对应)

结构来源: /api/v1/game/player/info 接口真实响应
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any
from dataclasses_json import dataclass_json, LetterCase, config


# ────────────────── 子结构 ──────────────────

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Avatar:
    type: str = ""
    id: str = ""
    url: str = ""


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Secretary:
    char_id: str = ""
    skin_id: str = ""


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApInfo:
    """理智信息"""
    current: int = 0
    max: int = 0
    last_ap_add_time: int = 0
    complete_recovery_time: int = 0


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ExpInfo:
    """经验值信息"""
    current: int = 0
    max: int = 0


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PlayerStatus:
    """玩家基础状态"""
    uid: str = ""
    name: str = ""
    level: int = 0
    avatar: Optional[Avatar] = None
    register_ts: int = 0
    main_stage_progress: str = ""
    secretary: Optional[Secretary] = None
    resume: str = ""
    subscription_end: int = 0
    ap: Optional[ApInfo] = None
    store_ts: int = 0
    last_online_ts: int = 0
    char_cnt: int = 0
    furniture_cnt: int = 0
    skin_cnt: int = 0
    exp: Optional[ExpInfo] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CharSkill:
    """干员技能"""
    id: str = ""
    specialize_level: int = 0


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CharEquip:
    """干员模组/装备"""
    id: str = ""
    level: int = 0
    locked: bool = False


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Char:
    """干员"""
    char_id: str = ""
    skin_id: str = ""
    level: int = 0
    evolve_phase: int = 0          # 精英化阶段 0/1/2
    potential_rank: int = 0        # 潜能等级 0-5
    main_skill_lvl: int = 1        # 技能等级
    skills: List[CharSkill] = field(default_factory=list)
    equip: List[CharEquip] = field(default_factory=list)
    favor_percent: int = 0         # 信赖度 (百分比，200=满)
    default_skill_id: str = ""
    gain_time: int = 0
    default_equip_id: str = ""
    sort_id: int = 0
    exp: int = 0
    gold: int = 0
    rarity: int = 0


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AssistChar:
    """助战干员"""
    char_id: str = ""
    skin_id: str = ""
    level: int = 0
    evolve_phase: int = 0
    potential_rank: int = 0
    skill_id: str = ""
    main_skill_lvl: int = 1
    specialize_level: int = 0
    equip: Optional[CharEquip] = None


# ────────────────── 顶层响应 ──────────────────

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PlayerInfo:
    """
    /api/v1/game/player/info 响应结构。
    包含玩家状态、干员列表、勋章等核心数据。
    """
    current_ts: int = 0
    status: Optional[PlayerStatus] = None
    chars: List[Char] = field(default_factory=list)
    assist_chars: List[AssistChar] = field(default_factory=list)
    # building / recruit / medal 等字段较复杂或玩家可选隐藏，用 Any 跳过类型推断
    building: Optional[Any] = None
    recruit: Optional[Any] = None
    medal: Optional[Any] = None
    show_config: Optional[Any] = None
