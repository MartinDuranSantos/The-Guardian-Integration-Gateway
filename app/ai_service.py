import asyncio


class AiService:
    """
    Simulates an external AI provider call.
    """

    @staticmethod
    async def generate_answer(sanitized_message: str) -> str:
        """
        Mock AI call with a 2-second network delay.
        In production, this would call OpenAI, Anthropic, etc.
        """
        await asyncio.sleep(2)  # Simulates latency
        return "Generated Answer."