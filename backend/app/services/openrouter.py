"""Unified OpenRouter client: one wrapper for every LLM/image task, so swapping
a model later is a one-line change to config.py rather than a code change here.
"""

import json

import httpx

from app.config import settings

_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


_COMPETITORS_SCHEMA = {
    "name": "competitors",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "resolved_name": {"type": "string"},
            "competitors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "domain": {"type": ["string", "null"]},
                        "logo_url": {"type": ["string", "null"]},
                    },
                    "required": ["name", "domain", "logo_url"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["resolved_name", "competitors"],
        "additionalProperties": False,
    },
}

_ADS_SCHEMA = {
    "name": "ads",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "ads": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "headlines": {"type": "array", "items": {"type": "string"}},
                        "descriptions": {"type": "array", "items": {"type": "string"}},
                        "differentiation": {"type": "string"},
                        "reasoning": {"type": "string"},
                    },
                    "required": ["headlines", "descriptions", "differentiation", "reasoning"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["ads"],
        "additionalProperties": False,
    },
}


async def _chat_completion(model: str, messages: list[dict], schema: dict) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            _BASE_URL,
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "response_format": {"type": "json_schema", "json_schema": schema},
            },
        )
        if response.is_error:
            raise RuntimeError(f"OpenRouter {response.status_code} error: {response.text}")
        data = response.json()
        return data["choices"][0]["message"]["content"]


def _parse_json(raw: str) -> dict:
    # models occasionally wrap JSON in ```json fences despite instructions
    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(cleaned)


async def get_competitors(company_name: str) -> dict:
    """Returns {"resolved_name": str, "competitors": [{"name", "domain", "logo_url"}, ...] (exactly 3)}"""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a market research analyst with live web search. Given a company name, "
                "resolve it to its canonical company name and identify exactly 3 direct competitors "
                "currently operating in the same market."
            ),
        },
        {"role": "user", "content": company_name},
    ]
    raw = await _chat_completion(settings.openrouter_competitor_model, messages, _COMPETITORS_SCHEMA)
    return _parse_json(raw)


def _format_competitor_ads(competitor_ads: list[dict]) -> str:
    if not competitor_ads:
        return "No competitor ads were available for grounding."
    lines = []
    for ad in competitor_ads:
        headline = ad.get("headline") or "(no headline)"
        body = ad.get("body_text") or "(no body text)"
        lines.append(f"- [{ad.get('source', 'unknown')}] {headline} — {body}")
    return "\n".join(lines)


async def generate_ads(company_name: str, competitor_ads: list[dict], context: str | None = None) -> list[dict]:
    """Returns a list of exactly 3 dicts:
    {"headlines": [str], "descriptions": [str], "differentiation": str, "reasoning": str}
    """
    competitor_ad_context = _format_competitor_ads(competitor_ads)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a senior performance marketing copywriter. You will be given a company name, "
                "optional extra context, and a sample of ads its competitors are currently running. "
                "Generate exactly 3 distinct original ad concepts for the company (not the competitors). "
                "For each concept, provide:\n"
                "- headlines: 3-5 short headline variants (Google RSA style, <=30 chars each)\n"
                "- descriptions: 2-4 description variants (<=90 chars each)\n"
                "- differentiation: what makes this company better/stand out vs. the competitor ads shown "
                "above — be concrete and specific, grounded in the actual competitor copy, not generic claims\n"
                "- reasoning: why this specific angle/hook should work — the persuasion logic (pain point "
                "targeted, positioning gap it exploits, etc.)\n\n"
                "Generate exactly 3 ad concepts."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Company: {company_name}\n\n"
                f"Extra context: {context or '(none)'}\n\n"
                f"Competitor ads currently running:\n{competitor_ad_context}"
            ),
        },
    ]
    raw = await _chat_completion(settings.openrouter_copy_model, messages, _ADS_SCHEMA)
    parsed = _parse_json(raw)
    return parsed["ads"]


async def generate_image(prompt: str) -> str:
    """Ad image generation via Nano Banana (google/gemini-2.5-flash-image).

    Not wired into any router yet — image_url stays optional on GeneratedAd until this
    is needed (build order step 4, image gen is marked optional there).
    """
    raise NotImplementedError("Image generation is not yet wired up for this demo.")
