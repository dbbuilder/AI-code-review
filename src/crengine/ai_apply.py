from typing import Literal, List
from tenacity import retry, stop_after_attempt, wait_exponential

Provider = Literal["openai","anthropic","gemini"]

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def propose_patches(provider: Provider, model: str, prompts: List[str]) -> List[str]:
    if provider == "openai":
        from openai import OpenAI
        client = OpenAI()
        outs = []
        for p in prompts:
            r = client.responses.create(model=model, input=p)  # Responses API
            outs.append(r.output_text)
        return outs
    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
        outs = []
        for p in prompts:
            msg = client.messages.create(model=model, max_tokens=2000, messages=[{"role":"user","content":p}])
            outs.append(msg.content[0].text)
        return outs
    elif provider == "gemini":
        from google import genai
        client = genai.Client()
        outs = []
        for p in prompts:
            resp = client.models.generate_content(model=model, contents=p)
            outs.append(resp.text)
        return outs
    else:
        raise ValueError("Unsupported provider")
