
from enum import Enum
from typing import List, Dict, Set

class State(str, Enum):
    START = "start"
    ID = "id_check"
    DOC = "doc_check"
    CLOSE = "close"

EXPECTED: Dict[State, List[str]] = {
    State.START: ["挨拶","用件確認"],
    State.ID: ["本人確認"],
    State.DOC: ["必要書類案内","再来防止提案"],
    State.CLOSE: ["理解確認","お礼"]
}

def check_slots(state: State, user_text: str) -> Set[str]:
    text = (user_text or "").lower()
    s = set()
    if state == State.START:
        if any(k in text for k in ["住民票", "用件", "発行", "ください", "取りに", "欲しい","申請"]):
            s.add("用件確認")
    if state == State.ID:
        if any(k in text for k in ["身分証", "免許", "マイナンバー", "在留カード", "保険証"]):
            s.add("本人確認")
    if state == State.DOC:
        if any(k in text for k in ["必要", "書類", "手数料", "300", "200","受付時間"]):
            s.add("必要書類案内")
        if any(k in text for k in ["コンビニ", "オンライン", "再来", "マイナポータル","予約"]):
            s.add("再来防止提案")
    if state == State.CLOSE:
        if any(k in text for k in ["大丈夫", "わかりました", "理解", "以上","問題ない"]):
            s.add("理解確認")
        if any(k in text for k in ["ありがとう", "失礼します", "お願いします"]):
            s.add("お礼")
    return s

def next_state(state: State, satisfied: Set[str]) -> State:
    if state == State.START and "用件確認" in satisfied:
        return State.ID
    if state == State.ID and "本人確認" in satisfied:
        return State.DOC
    if state == State.DOC and {"必要書類案内","再来防止提案"}.issubset(satisfied):
        return State.CLOSE
    if state == State.CLOSE and {"理解確認","お礼"}.issubset(satisfied):
        return State.CLOSE
    return state
