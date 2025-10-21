
from fastapi import APIRouter
from backend.models.schemas import ScoreRequest
from backend.core import rubric, llm
from pathlib import Path
import json

router = APIRouter()

@router.post("/evaluate")
def evaluate(req: ScoreRequest):
    rule_part = rubric.evaluate_conversation([t.dict() for t in req.conversation])
    rb_path = Path(__file__).resolve().parents[1] / "data" / "rubric_basic.json"
    rubric_json = json.loads(rb_path.read_text(encoding="utf-8")) if rb_path.exists() else {}
    llm_part = llm.grade_conversation([t.dict() for t in req.conversation], rubric_json)

    total_rule = rule_part.get("total_score", 0)
    total_llm = llm_part.get("total_score", 0)
    total = round(total_rule * 0.7 + total_llm * 0.3, 1) if total_rule and total_llm else (total_rule or total_llm)

    return {
        "total_score": total,
        "rule_based": rule_part,
        "llm_based": llm_part
    }
