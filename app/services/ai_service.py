import asyncio


class AiService:
    """
    Simulates an external AI provider call.
    """

    _force_failure = False  # Toggle to True to simulate AI outages

    @staticmethod
    async def generate_answer(sanitized_message: str) -> str:
        """
        Mock AI call with a 2-second network delay.
        In production, this would call OpenAI, Anthropic, etc.
        """

        if AiService._force_failure:
            raise ConnectionError("Mock AI service is down")
        await asyncio.sleep(2)  # Simulates 2-second network latency
        return "Generated Answer."