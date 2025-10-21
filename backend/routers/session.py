
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.models.schemas import HearRequest, HearResponse, State, HearAudioResponse
from backend.core import fsm, stt, tts, llm
from pathlib import Path
import base64, json

router = APIRouter()

def _pending_requirements(state: str, satisfied: set):
    m = {
        "start": ["挨拶","用件確認"],
        "id_check": ["本人確認"],
        "doc_check": ["必要書類案内","再来防止提案"],
        "close": ["理解確認","お礼"]
    }
    return [x for x in m.get(state, []) if x not in satisfied]

def _load_scenario(scenario_id: str | None):
    path = Path(__file__).resolve().parents[1] / "data" / "scenarios_it.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"scenarios":[]}
    if not scenario_id and data["scenarios"]:
        return data["scenarios"][0]
    for s in data["scenarios"]:
        if s["id"] == scenario_id:
            return s
    return None

@router.post("/hear", response_model=HearResponse)
def hear(req: HearRequest):
    scenario = _load_scenario(req.scenario_id)
    trap_cards = scenario.get("trap_cards", []) if scenario else []
    satisfied = fsm.check_slots(fsm.State(req.state), req.user_text)
    pending = _pending_requirements(req.state, satisfied)
    agent_text = llm.generate_agent_reply(req.state, req.user_text, pending, trap_cards)
    next_state = fsm.next_state(fsm.State(req.state), satisfied)
    return HearResponse(next_state=next_state, agent_text=agent_text)

@router.post("/hear_audio", response_model=HearAudioResponse)
async def hear_audio(state: State = Form(...), audio: UploadFile = File(...), scenario_id: str | None = Form(None)):
    if not audio: raise HTTPException(status_code=400, detail="audio file is required")
    wav_bytes = await audio.read()
    user_text = stt.wav_bytes_to_text(wav_bytes, language="ja")
    scenario = _load_scenario(scenario_id)
    trap_cards = scenario.get("trap_cards", []) if scenario else []
    satisfied = fsm.check_slots(fsm.State(state), user_text)
    pending = _pending_requirements(state, satisfied)
    agent_text = llm.generate_agent_reply(state, user_text, pending, trap_cards)
    next_state = fsm.next_state(fsm.State(state), satisfied)
    try:
        agent_wav = tts.synthesize_to_wav(agent_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {e}")
    b64 = base64.b64encode(agent_wav).decode("utf-8")
    return HearAudioResponse(next_state=next_state, user_text=user_text, agent_text=agent_text, agent_audio_wav_base64=b64)
