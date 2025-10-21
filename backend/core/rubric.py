
import json
from typing import List, Dict, Any
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RUBRIC = json.loads((DATA_DIR / "rubric_basic.json").read_text(encoding="utf-8"))

def evaluate_conversation(conversation: List[Dict[str, str]]):
    txt_user = "\n".join([u["text"] for u in conversation if u["who"] == "user"]).lower()
    def has_any(keys):
        return any(k.lower() in txt_user for k in keys)

    sub = {}
    total = 0.0
    detail = {}

    for key, rule in RUBRIC.items():
        must = rule.get("must", [])
        satisfied = 0
        for m in must:
            syms = [s.strip() for s in m.split("||")]
            satisfied += 1 if has_any(syms) else 0
        ratio = satisfied / max(1, len(must))
        sub_score = 1 + ratio * 4
        sub[key] = round(sub_score, 2)
        detail[key] = {"satisfied": satisfied, "required": len(must), "ratio": round(ratio, 2)}
        total += sub_score * rule.get("weight", 1.0)

    max_total = sum(5.0 * r.get("weight",1.0) for r in RUBRIC.values())
    total_norm = round(100.0 * total / max_total, 1)

    improvements = []
    for key, rule in RUBRIC.items():
        if detail[key]["ratio"] < 1.0:
            improvements.append(f"{rule['name']}: {rule.get('hint','この項目の要件を満たしましょう')}")

    return {"total_score": total_norm, "sub_scores": sub, "improvements": improvements[:5]}
