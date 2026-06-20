"""
SCP Archive AI Guide - Powered by Anthropic Claude.
Provides intelligent assistance for exploring the SCP Foundation universe.
"""

import json
import os
from typing import Optional
from anthropic import Anthropic

SYSTEM_PROMPT = """You are the SCP Foundation Archivist AI, an intelligent guide to the SCP Foundation universe. 
You have access to a database of SCP articles, Foundation Tales, and Groups of Interest (GOI) formats.

Your role is to:
1. **Explain SCP lore** - Answer questions about specific SCPs, their containment procedures, properties, and significance
2. **Make recommendations** - Suggest SCPs based on interests, themes, or desired characteristics
3. **Guide through narratives** - Explain canon connections, storyline arcs, and how different SCPs relate
4. **Help with search** - Help users find specific SCPs based on natural language descriptions
5. **Provide context** - Explain the Foundation universe, terminology, GOIs, and narrative canons

Guidelines:
- Be accurate and cite specific SCP numbers when referencing entries
- Distinguish between canon facts and interpretations
- Note when something is from a specific canon or tale
- Maintain the in-universe tone when appropriate (clinical, professional, slightly ominous)
- If you don't know something, say so rather than making it up
- Keep responses informative but concise

The database contains:
- SCP Articles: Numbered anomaly files with object class, containment procedures, and descriptions
- Foundation Tales: Narrative stories set in the SCP universe
- GOI Formats: Documents from Groups of Interest (like the Church of the Broken God, Serpent's Hand, etc.)
"""


class AIGuide:
    """AI-powered SCP Foundation guide using Anthropic Claude."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None

    def is_available(self) -> bool:
        """Check if the AI guide is configured and available."""
        return self.client is not None

    def ask(self, question: str, context: Optional[list[dict]] = None) -> str:
        """Ask the AI guide a question about the SCP universe."""
        if not self.is_available():
            return "The AI Guide is not configured. Set your ANTHROPIC_API_KEY environment variable to enable it."

        messages = []

        # Add context entries if provided
        if context:
            context_block = "Here are relevant SCP entries for context:\n\n"
            for entry in context[:5]:
                context_block += f"--- {entry.get('id', 'Unknown')}: {entry.get('title', '')} ---\n"
                context_block += f"Object Class: {entry.get('object_class', 'N/A')}\n"
                if entry.get('containment_procedures'):
                    context_block += f"Containment: {entry.get('containment_procedures', '')[:300]}\n"
                context_block += f"Description: {entry.get('description', '')[:500]}\n\n"
            messages.append({"role": "user", "content": context_block})

        messages.append({"role": "user", "content": question})

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                system=SYSTEM_PROMPT,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            return response.content[0].text if response.content else ""
        except Exception as e:
            return f"Error querying AI Guide: {str(e)}"

    def recommend(self, scp_id: str, title: str, tags: list[str], description: str) -> str:
        """Get recommendations based on an SCP's characteristics."""
        if not self.is_available():
            return self._fallback_recommendation(tags)

        prompt = (
            f"I'm interested in {scp_id} - {title}. "
            f"Its tags are: {', '.join(tags)}. "
            f"Description: {description[:500]}\n\n"
            "Based on this SCP's themes, object class, and characteristics, "
            "recommend 3-5 other SCPs I would likely enjoy. "
            "Explain why each recommendation fits my interests."
        )

        return self.ask(prompt)

    def _fallback_recommendation(self, tags: list[str]) -> str:
        """Fallback recommendation when Claude is not available."""
        tag_based = {
            "keter": "SCP-682 (Hard-to-Destroy Reptile) - The iconic unkillable lizard",
            "euclid": "SCP-173 (The Sculpture) - The classic that started it all",
            "safe": "SCP-999 (The Tickle Monster) - A friendly slime that makes you happy",
            "thaumiel": "SCP-2000 (The Deus Ex Machina) - A reality-restoring machine",
            "humanoid": "SCP-096 (The Shy Guy) - A humanoid with a deadly reaction",
            "living": "SCP-939 (With Many Voices) - Pack-predators that mimic human speech",
        }
        
        matches = [tag_based.get(t.lower(), "") for t in tags if t.lower() in tag_based]
        if matches:
            return "Based on your interests, I recommend:\n\n" + "\n".join(f"• {m}" for m in matches[:5])
        return (
            "Based on popular SCPs, I recommend checking out:\n"
            "• SCP-173 (The Sculpture)\n"
            "• SCP-682 (Hard-to-Destroy Reptile)\n"
            "• SCP-999 (The Tickle Monster)\n"
            "• SCP-096 (The Shy Guy)\n"
            "• SCP-914 (The Clockworks)"
        )

    def smart_search(self, query: str, db_session=None) -> dict:
        """Interpret natural language search queries into structured filters."""
        if not self.is_available() or not db_session:
            return {"query": query, "interpretation": None}

        prompt = (
            f"Convert this natural language search into structured database filters: '{query}'\n\n"
            "Respond with ONLY a JSON object with these fields:\n"
            "{\n"
            '  "object_class": "class name or null",\n'
            '  "entry_type": "scp or tale or goi-format or null",\n'
            '  "tags": ["array of relevant tags"],\n'
            '  "keywords": "search text",\n'
            '  "series": series_number_or_null,\n'
            '  "explanation": "brief explanation"\n'
            "}"
        )

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1,
            )
            text = response.content[0].text if response.content else "{}"
            # Extract JSON from the response
            json_match = __import__('re').search(r'\{.*\}', text, __import__('re').DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {"query": query, "interpretation": result}
            return {"query": query, "interpretation": None}
        except Exception:
            return {"query": query, "interpretation": None}