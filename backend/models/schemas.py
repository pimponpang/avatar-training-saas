
from pydantic import BaseModel
from typing import Literal, List, Dict, Any

State = Literal["start", "id_check", "doc_check", "close"]

class HearRequest(BaseModel):
    state: State
    user_text: str
    scenario_id: str | None = None

class HearResponse(BaseModel):
    next_state: State
    agent_text: str

class HearAudioResponse(BaseModel):
    next_state: State
    user_text: str
    agent_text: str
    agent_audio_wav_base64: str

class Turn(BaseModel):
    who: Literal["user","agent"]
    text: str

class ScoreRequest(BaseModel):
    conversation: List[Turn]
