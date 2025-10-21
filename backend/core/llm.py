
import os, json, re
from typing import List, Dict, Any
from pathlib import Path

# LLM = Large Language Model（大規模言語モデル）
# OpenAI互換 (OpenAI / Azure OpenAI / LM Studio 等)
def _get_client():
    from openai import OpenAI
    base = os.getenv("OPENAI_BASE_URL")
    if base:
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=base)
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def _kb() -> str:
    p = Path(__file__).resolve().parents[1] / "data" / "knowledge.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""

def generate_agent_reply(state: str, user_text: str, pending: List[str], trap_cards: List[str]) -> str:
    client = _get_client()
    system = f"""あなたは市役所の来庁者としてロールプレイするAIです。
- 返答は 1〜2文。専門用語は平易に。
- {', '.join(trap_cards) if trap_cards else '穏当'} の範囲で感情を調整（過度に過激にしない）。
- knowledge.mdの範囲外の制度説明はしない（不明は「確認します」）。
- 目的は職員に必要な手順を言わせること。未達は促す。
state: {state} / 未達: {', '.join(pending) if pending else 'なし'}"""
    user = f"相手（職員）の直前発話: {user_text}\nあなた（来庁者）として自然に返答してください。"
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role":"system","content":system},
            {"role":"user","content":_kb()},
            {"role":"user","content":user},
        ],
        temperature=0.4, max_tokens=120,
    )
    return resp.choices[0].message.content.strip()

def grade_conversation(conversation: List[Dict[str,str]], rubric: Dict[str,Any]) -> Dict[str, Any]:
    client = _get_client()
    rubric_text = json.dumps(rubric, ensure_ascii=False)
    convo_text = "\n".join([f"{t['who']}: {t['text']}" for t in conversation])
    system = """あなたは市役所窓口の教育担当です。以下の会話ログを採点します。
- ルーブリックに基づき A..G を 1〜5点で採点
- 総合点 total_score を 0〜100 で算出
- 各指摘には根拠抜粋（10〜30字）を付ける
- 出力は JSON のみ
"""
    user = f"""ルーブリック: {rubric_text}
会話ログ:
{convo_text}

出力:
{{
  "total_score": <number>,
  "sub_scores": {{"A":<1-5>,"B":<1-5>,"C":<1-5>,"D":<1-5>,"E":<1-5>,"F":<1-5>,"G":<1-5>}},
  "strengths": ["..."],
  "improvements": [{{"label":"...", "reason":"(抜粋)", "tip":"改善フレーズ"}}]
}}
"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=0.2, max_tokens=600,
    )
    txt = resp.choices[0].message.content
    m = re.search(r"\{[\s\S]*\}\s*$", txt)
    if m: txt = m.group(0)
    try:
        return json.loads(txt)
    except Exception:
        return {"total_score": 0, "sub_scores": {}, "strengths": [], "improvements": [{"label":"出力エラー","reason":"JSON解析失敗","tip":"プロンプト調整"}]}
