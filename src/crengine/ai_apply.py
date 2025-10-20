"""AI provider integration with rate limiting, cost tracking, and retry logic."""
import time
from typing import Literal, List, Dict, Any, Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

Provider = Literal["openai", "anthropic", "gemini"]


class RateLimiter:
    """Simple rate limiter to enforce minimum delay between API calls."""

    def __init__(self, rate_limit_rps: float):
        """
        Initialize rate limiter.

        Args:
            rate_limit_rps: Maximum requests per second (e.g., 2.0 = 2 requests/sec)
        """
        self.rate_limit_rps = rate_limit_rps
        self.min_interval = 1.0 / rate_limit_rps if rate_limit_rps > 0 else 0
        self.last_call_time = 0.0

    def wait(self):
        """Wait if necessary to respect rate limit."""
        if self.min_interval == 0:
            return

        current_time = time.time()
        time_since_last = current_time - self.last_call_time

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_call_time = time.time()


# Cost per 1K tokens (as of 2025)
PRICING = {
    "openai": {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # GPT-4o mini pricing
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "default": {"input": 0.00015, "output": 0.0006}  # Default to GPT-4o-mini pricing
    },
    "anthropic": {
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-5-haiku-20241022": {"input": 0.001, "output": 0.005},  # Claude 3.5 Haiku pricing
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
        "default": {"input": 0.001, "output": 0.005}  # Default to Haiku pricing
    },
    "gemini": {
        "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
        "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
        "default": {"input": 0.000075, "output": 0.0003}  # Default to Flash pricing
    }
}


def estimate_cost(
    provider: Provider,
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Estimate cost for API call.

    Args:
        provider: AI provider name
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Estimated cost in USD
    """
    provider_pricing = PRICING.get(provider, {})
    model_pricing = provider_pricing.get(model, provider_pricing.get("default", {"input": 0, "output": 0}))

    input_cost = (input_tokens / 1000) * model_pricing["input"]
    output_cost = (output_tokens / 1000) * model_pricing["output"]

    return input_cost + output_cost


def _call_openai(
    model: str,
    prompts: List[str],
    max_output_tokens: int,
    temperature: float,
    rate_limiter: RateLimiter
) -> Tuple[List[str], Dict[str, Any]]:
    """
    Call OpenAI API with rate limiting and cost tracking.

    Args:
        model: Model name (e.g., "gpt-4")
        prompts: List of prompts
        max_output_tokens: Maximum tokens per response
        temperature: Sampling temperature
        rate_limiter: Rate limiter instance

    Returns:
        Tuple of (responses, cost_info)
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install 'code-review-engine[ai]'")

    client = OpenAI()
    outputs = []
    total_input_tokens = 0
    total_output_tokens = 0

    for prompt in prompts:
        rate_limiter.wait()

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        outputs.append(response.choices[0].message.content)

        # Track token usage
        if hasattr(response, 'usage'):
            total_input_tokens += response.usage.prompt_tokens
            total_output_tokens += response.usage.completion_tokens

    total_cost = estimate_cost("openai", model, total_input_tokens, total_output_tokens)

    cost_info = {
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "total_cost": total_cost,
        "cost_per_request": total_cost / len(prompts) if prompts else 0
    }

    return outputs, cost_info


def _call_anthropic(
    model: str,
    prompts: List[str],
    max_output_tokens: int,
    temperature: float,
    rate_limiter: RateLimiter
) -> Tuple[List[str], Dict[str, Any]]:
    """
    Call Anthropic API with rate limiting and cost tracking.

    Args:
        model: Model name (e.g., "claude-3-5-sonnet-20241022")
        prompts: List of prompts
        max_output_tokens: Maximum tokens per response
        temperature: Sampling temperature
        rate_limiter: Rate limiter instance

    Returns:
        Tuple of (responses, cost_info)
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install 'code-review-engine[ai]'")

    client = anthropic.Anthropic()
    outputs = []
    total_input_tokens = 0
    total_output_tokens = 0

    for prompt in prompts:
        rate_limiter.wait()

        message = client.messages.create(
            model=model,
            max_tokens=max_output_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        outputs.append(message.content[0].text)

        # Track token usage
        if hasattr(message, 'usage'):
            total_input_tokens += message.usage.input_tokens
            total_output_tokens += message.usage.output_tokens

    total_cost = estimate_cost("anthropic", model, total_input_tokens, total_output_tokens)

    cost_info = {
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "total_cost": total_cost,
        "cost_per_request": total_cost / len(prompts) if prompts else 0
    }

    return outputs, cost_info


def _call_gemini(
    model: str,
    prompts: List[str],
    max_output_tokens: int,
    temperature: float,
    rate_limiter: RateLimiter
) -> Tuple[List[str], Dict[str, Any]]:
    """
    Call Google Gemini API with rate limiting and cost tracking.

    Args:
        model: Model name (e.g., "gemini-1.5-pro")
        prompts: List of prompts
        max_output_tokens: Maximum tokens per response
        temperature: Sampling temperature
        rate_limiter: Rate limiter instance

    Returns:
        Tuple of (responses, cost_info)
    """
    try:
        from google import genai
    except ImportError:
        raise ImportError("google-genai package not installed. Run: pip install 'code-review-engine[ai]'")

    client = genai.Client()
    outputs = []
    total_input_tokens = 0
    total_output_tokens = 0

    for prompt in prompts:
        rate_limiter.wait()

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            generation_config={
                "max_output_tokens": max_output_tokens,
                "temperature": temperature
            }
        )

        outputs.append(response.text)

        # Track token usage (Gemini provides usage metadata)
        if hasattr(response, 'usage_metadata'):
            total_input_tokens += response.usage_metadata.prompt_token_count
            total_output_tokens += response.usage_metadata.candidates_token_count

    total_cost = estimate_cost("gemini", model, total_input_tokens, total_output_tokens)

    cost_info = {
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "total_cost": total_cost,
        "cost_per_request": total_cost / len(prompts) if prompts else 0
    }

    return outputs, cost_info


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((Exception,))  # Retry on rate limits and transient errors
)
def propose_patches(
    provider: Provider,
    model: str,
    prompts: List[str],
    max_output_tokens: int = 2000,
    temperature: float = 0.2,
    rate_limit_rps: float = 1.0,
    return_cost: bool = False
) -> Any:
    """
    Generate code patches using AI provider.

    Args:
        provider: AI provider ("openai", "anthropic", "gemini")
        model: Model name
        prompts: List of prompts for patch generation
        max_output_tokens: Maximum tokens per response (default: 2000)
        temperature: Sampling temperature (default: 0.2 for deterministic)
        rate_limit_rps: Rate limit in requests per second (default: 1.0)
        return_cost: If True, return (responses, cost_info) tuple

    Returns:
        List of patch strings, or (patches, cost_info) if return_cost=True

    Raises:
        ImportError: If required AI SDK not installed
        ValueError: If unsupported provider
        Various API errors from providers (with retry)
    """
    if not prompts:
        return ([], {}) if return_cost else []

    rate_limiter = RateLimiter(rate_limit_rps)

    if provider == "openai":
        outputs, cost_info = _call_openai(model, prompts, max_output_tokens, temperature, rate_limiter)
    elif provider == "anthropic":
        outputs, cost_info = _call_anthropic(model, prompts, max_output_tokens, temperature, rate_limiter)
    elif provider == "gemini":
        outputs, cost_info = _call_gemini(model, prompts, max_output_tokens, temperature, rate_limiter)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    if return_cost:
        return outputs, cost_info
    return outputs
