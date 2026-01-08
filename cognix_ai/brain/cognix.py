# brain/cognix.py

import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config import settings


class CognixAI:
    def __init__(self, tools: dict, memory: list | None = None):
        """
        tools: dict[str, callable]
        memory: conversational memory (non-authoritative)
        """
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
            "visit",
            "go to",
            "then",
            "instead",
            "change",
            "update",
            "remove",
            "add",
            "start",
            "set the date",
            "set date",
            "reschedule"
        ])

    def _should_use_rag(self, text: str) -> bool:
        text = text.lower()
        return any(k in text for k in [
            "restaurant",
            "food",
            "eat",
            "dining",
            "cuisine",
            "local food",
            "cafes",
            "bars"
        ])

    # ============================================================
    # DRAFT ITINERARY UPDATE (LLM REASONING ONLY)
    # ============================================================

    def _update_draft_itinerary(self, user_input: str, context: dict) -> list:
        """
        Takes existing draft (from DB) and applies user changes.
        """
        prompt = f"""
You are an itinerary editor.

Current itinerary:
{context.get("draft_itinerary", [])}

User request:
"{user_input}"

Return ONLY valid JSON in this exact format:
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
- Preserve all existing steps unless explicitly changed
- If user sets a date globally, apply it to ALL steps
- If user changes time for a location, update ONLY that location
- Date or time may be "unknown"
- Do NOT invent new locations unless explicitly requested
"""

        raw = self.llm.invoke(prompt).content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(raw)
        return parsed.get("draft_itinerary", [])

    # ============================================================
    # TOOL DECISION (NON-ITINERARY)
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
    # FINAL RESPONSE SYNTHESIS (FIXES CHAT STAMMERING)
    # ============================================================

    def _synthesize_chat(self, user_input: str, context: dict, tool_results: dict) -> str:
        prompt = f"""
You are Cognix AI, a confident travel assistant.

Answer naturally and directly.

You may use:
- Tool results
- Known context (place, itinerary, weather)
- Your own general knowledge if data is missing

DO NOT:
- Ask for more context
- Say "I don't know where you are"
- Mention tools or internal logic

User question:
"{user_input}"

Context:
Place: {context.get("place")}
Itinerary: {context.get("draft_itinerary")}
Tool results: {tool_results}
"""
        return self.llm.invoke(prompt).content

    # ============================================================
    # MAIN ENTRY POINT
    # ============================================================

    def run(self, user_input: str, context: dict):
        """
        Returns:
        - dict (draft / finalize)
        - str (chat)
        """

        # ---------------- FINALIZE (WITH OR WITHOUT EDIT) ----------------
        if self._is_finalize_intent(user_input):

            # allow "set date and finalize" in ONE message
            if self._is_draft_edit_intent(user_input):
                updated = self._update_draft_itinerary(user_input, context)
                context["draft_itinerary"] = updated

            if not context.get("draft_itinerary"):
                return "You don’t have any plan yet to finalize."

            result = self.tools["ITINERARY"](user_input, context)

            return {
                "status": "finalized",
                "message": result,
                "itinerary": context.get("draft_itinerary")
            }

        # ---------------- DRAFT EDIT ----------------
        if self._is_draft_edit_intent(user_input):
            updated = self._update_draft_itinerary(user_input, context)
            context["draft_itinerary"] = updated
            self.memory.append(user_input)

            return {
                "draft_itinerary": updated,
                "message": "Got it. I’ve updated your draft plan. Say ‘finalize’ when ready."
            }

        # ---------------- RAG PRIORITY (FOOD / LOCAL FACTS) ----------------
        if self._should_use_rag(user_input) and "RAG" in self.tools:
            rag_data = self.tools["RAG"](user_input, context)
            return self._synthesize_chat(user_input, context, {"RAG": rag_data})

        # ---------------- NORMAL TOOL FLOW ----------------
        tool_results = {}
        for tool in self._decide_tools(user_input):
            tool_results[tool] = self.tools[tool](user_input, context)

        if tool_results:
            return self._synthesize_chat(user_input, context, tool_results)

        # ---------------- PURE CHAT FALLBACK ----------------
        return self.llm.invoke(user_input).content