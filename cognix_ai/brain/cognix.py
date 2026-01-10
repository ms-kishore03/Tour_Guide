# brain/cognix.py

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config import settings


class CognixAI:
    def __init__(self, tools: dict, memory: list | None = None):
        self.tools = tools
        self.memory = memory or []
        self.llm = settings.llm

    # ============================================================
    # INTENT DETECTION
    # ============================================================

    def _is_finalize_intent(self, text: str) -> bool:
        text = text.lower()
        return any(k in text for k in [
            "finalize",
            "final plan",
            "confirm itinerary",
            "save my plan",
            "this is my final plan"
        ])

    def _is_draft_edit_intent(self, text: str) -> bool:
        text = text.lower()
        return any(k in text for k in [
            "visit", "go to", "then", "instead",
            "change", "update", "remove", "add",
            "start", "set the date", "set date",
            "reschedule"
        ])

    def _is_weather_intent(self, text: str) -> bool:
        text = text.lower()
        return any(k in text for k in [
            "weather", "temperature", "forecast",
            "rain", "rainfall", "humidity",
            "hot", "cold", "climate", "wind"
        ])

    def _should_use_rag(self, text: str) -> bool:
        text = text.lower()
        return any(k in text for k in [
            "restaurant", "food", "eat",
            "dining", "cuisine", "cafes", "bars"
        ])

    # ============================================================
    # DRAFT UPDATE (LLM — NOT AUTHORITATIVE)
    # ============================================================

    def _update_draft_itinerary(self, user_input: str, context: dict) -> list:
        prompt = f"""
You are an itinerary editor.

Current itinerary:
{context.get("draft_itinerary", [])}

User request:
"{user_input}"

Return ONLY valid JSON:
{{
  "draft_itinerary": [
    {{
      "location": "<string>",
      "date": "<string>",
      "time": "<string>"
    }}
  ]
}}

Rules:
- Preserve existing steps unless explicitly changed
- If user sets a date globally, apply it to ALL steps
- If user changes time for a location, update ONLY that location
- Date or time may be "unknown"
- Do NOT invent new locations
"""

        raw = self.llm.invoke(prompt).content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        return parsed.get("draft_itinerary", [])

    # ============================================================
    # 🔒 AUTHORITATIVE NORMALIZATION + SORTING
    # ============================================================

    def _normalize_and_sort_itinerary(self, itinerary: list) -> list:
        today = datetime.today().strftime("%m/%d/%Y")

        def safe_parse_date(d):
            try:
                return datetime.strptime(d, "%m/%d/%Y")
            except Exception:
                return datetime.strptime(today, "%m/%d/%Y")

        def safe_parse_time(t):
            if t == "unknown":
                return (0, 0)
            try:
                dt = datetime.strptime(t.strip().upper(), "%I:%M %p")
                return (1, dt.hour * 60 + dt.minute)
            except Exception:
                return (1, 9999)

        # Normalize defaults
        for item in itinerary:
            if not item.get("date") or item["date"] == "unknown":
                item["date"] = today
            if not item.get("time"):
                item["time"] = "unknown"

        itinerary.sort(
            key=lambda x: (
                safe_parse_date(x["date"]),
                safe_parse_time(x["time"])
            )
        )

        return itinerary

    # ============================================================
    # DAY GROUPING (MULTI-DAY READY)
    # ============================================================

    def _group_itinerary_by_day(self, itinerary: list) -> dict:
        day_map = {}
        current_day = 1
        last_date = None

        for item in itinerary:
            date = item["date"]
            if date != last_date:
                day_map[f"Day {current_day}"] = []
                last_date = date
                current_day += 1
            day_map[f"Day {current_day - 1}"].append(item)

        return day_map

    # ============================================================
    # TOOL SELECTION (NON-ITINERARY)
    # ============================================================

    def _decide_tools(self, user_input: str) -> list[str]:
        prompt = f"""
Available tools:
{", ".join(self.tools.keys())}

User question:
"{user_input}"

Respond ONLY in this format:
TOOLS:
<comma separated tool names>

or

TOOLS:
NONE
"""
        decision = self.llm.invoke(prompt).content.strip()

        if "NONE" in decision:
            return []

        return [
            t.strip()
            for t in decision.replace("TOOLS:", "").split(",")
            if t.strip() in self.tools and t.strip() != "ITINERARY"
        ]

    # ============================================================
    # CHAT RESPONSE
    # ============================================================

    def _synthesize_chat(self, user_input: str, context: dict, tool_results: dict) -> str:
        prompt = f"""
You are Cognix AI, a confident travel assistant.

Answer naturally and directly.

User question:
"{user_input}"

Place: {context.get("place")}
Itinerary: {context.get("draft_itinerary")}
Tool results: {tool_results}
"""
        return self.llm.invoke(prompt).content

    # ============================================================
    # MAIN ENTRY
    # ============================================================

    def run(self, user_input: str, context: dict):

        # ---------------- WEATHER (HARD ROUTE) ----------------
        if self._is_weather_intent(user_input):
            if "WEATHER" not in self.tools:
                return "Weather service is unavailable at the moment."
            return self.tools["WEATHER"](user_input, context)

        # ---------------- FINALIZE ----------------
        if self._is_finalize_intent(user_input):

            if self._is_draft_edit_intent(user_input):
                proposed = self._update_draft_itinerary(user_input, context)
                context["draft_itinerary"] = proposed

            if not context.get("draft_itinerary"):
                return "You don’t have any plan yet to finalize."

            context["draft_itinerary"] = self._normalize_and_sort_itinerary(
                context["draft_itinerary"]
            )

            result = self.tools["ITINERARY"](user_input, context)

            grouped = self._group_itinerary_by_day(context["draft_itinerary"])

            return {
                "status": "finalized",
                "message": result,
                "itinerary": context["draft_itinerary"],
                "day_summary": grouped
            }

        # ---------------- DRAFT EDIT ----------------
        if self._is_draft_edit_intent(user_input):
            proposed = self._update_draft_itinerary(user_input, context)
            normalized = self._normalize_and_sort_itinerary(proposed)
            context["draft_itinerary"] = normalized
            self.memory.append(user_input)

            return {
                "draft_itinerary": normalized,
                "message": "Got it. I’ve updated your draft plan. Say ‘finalize’ when ready."
            }

        # ---------------- RAG ----------------
        if self._should_use_rag(user_input) and "RAG" in self.tools:
            rag = self.tools["RAG"](user_input, context)
            return self._synthesize_chat(user_input, context, {"RAG": rag})

        # ---------------- OTHER TOOLS ----------------
        results = {}
        for tool in self._decide_tools(user_input):
            results[tool] = self.tools[tool](user_input, context)

        if results:
            return self._synthesize_chat(user_input, context, results)

        # ---------------- FALLBACK ----------------
        return self.llm.invoke(user_input).content
