import json
import os


class GeminiProvider:
    def recommend_service_name(
        self,
        user_query: str,
        services: list[dict[str, str]],
        timeout_seconds: float = 8.0,
    ) -> dict[str, str | float | None]:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        try:
            import google.generativeai as genai
        except Exception as exc:
            raise RuntimeError("Gemini SDK is not available") from exc

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        service_lines = "\n".join(f"- {item['name']}: {item['description']}" for item in services)
        prompt = f"""
You are a Semantic Routing Engine for a health and aesthetics platform.
You will be provided with a list of available services and a user query in any language.
Your task is to map the user's intent to the MOST RELEVANT service from the provided list
based on semantic meaning and service descriptions.

Multilingual requirement:
- The user query may be in Hebrew, slang, or English.
- The service list is in English.
- You must understand multilingual intent and map to the correct English service name.

Allowed services:
{service_lines}

User query:
{user_query}

Return ONLY strict JSON in this format:
{{
  "matched_service_name": "<exact name from allowed services or null>",
  "location": "<city/area in English from user query or null>",
  "reason": "<short user-facing summary>",
  "explanation": "<professional justification of why this service matches, based on service descriptions>",
  "confidence_score": <number between 0 and 1>
}}
"""
        try:
            response = model.generate_content(
                prompt,
                request_options={"timeout": timeout_seconds},
            )
            raw_text = (response.text or "").strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`")
                raw_text = raw_text.replace("json", "", 1).strip()
            parsed = json.loads(raw_text)
        except Exception as exc:
            raise RuntimeError("Gemini request failed") from exc

        matched_raw = parsed.get("matched_service_name")
        matched_name = None if matched_raw is None else str(matched_raw).strip()
        location_raw = parsed.get("location")
        location = None if location_raw is None else str(location_raw).strip()
        if location == "":
            location = None
        reason = str(parsed.get("reason", "")).strip()
        explanation = str(parsed.get("explanation", "")).strip()
        confidence_score_raw = parsed.get("confidence_score", 0.0)
        try:
            confidence_score = float(confidence_score_raw)
        except Exception:
            confidence_score = 0.0
        confidence_score = max(0.0, min(1.0, confidence_score))
        if not reason:
            reason = "Consultation completed."
        if not explanation:
            explanation = "No detailed explanation provided by AI model."

        return {
            "matched_service_name": matched_name,
            "location": location,
            "reason": reason,
            "explanation": explanation,
            "confidence_score": confidence_score,
        }
