import json

from app.config import get_settings



def generate_audit_narrative(context: dict) -> dict[str, str] | None:
    settings = get_settings()
    if not settings.llm_enabled:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    try:
        client = OpenAI(**settings.openai_client_kwargs())
    except Exception:
        return None

    prompt = (
        "You are generating a demo payment-risk audit explanation. "
        "Never change the deterministic rule results. "
        "Never invent evidence sources or document names. "
        "Return strict JSON with keys summary and suggestion only."
    )

    try:
        completion = client.chat.completions.create(
            model=settings.active_model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": json.dumps(context, ensure_ascii=False, default=str),
                },
            ],
        )
        content = completion.choices[0].message.content or ""
        payload = json.loads(content)
    except Exception:
        return None

    summary = str(payload.get("summary", "")).strip()
    suggestion = str(payload.get("suggestion", "")).strip()

    if not summary or not suggestion:
        return None

    return {"summary": summary, "suggestion": suggestion}
