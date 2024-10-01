import hashlib
import json

import backoff

from aider.dump import dump  # noqa: F401
from aider.llm import litellm
from langfuse.decorators import observe, langfuse_context

# from diskcache import Cache


CACHE_PATH = "~/.aider.send.cache.v1"
CACHE = None
# CACHE = Cache(CACHE_PATH)

RETRY_TIMEOUT = 60


def retry_exceptions():
    import httpx

    return (
        httpx.ConnectError,
        httpx.RemoteProtocolError,
        httpx.ReadTimeout,
        litellm.exceptions.APIConnectionError,
        litellm.exceptions.APIError,
        litellm.exceptions.RateLimitError,
        litellm.exceptions.ServiceUnavailableError,
        litellm.exceptions.Timeout,
        litellm.exceptions.InternalServerError,
        litellm.llms.anthropic.chat.AnthropicError,
    )


def lazy_litellm_retry_decorator(func):
    def wrapper(*args, **kwargs):
        decorated_func = backoff.on_exception(
            backoff.expo,
            retry_exceptions(),
            max_time=RETRY_TIMEOUT,
            on_backoff=lambda details: print(
                f"{details.get('exception', 'Exception')}\nRetry in {details['wait']:.1f} seconds."
            ),
        )(func)
        return decorated_func(*args, **kwargs)

    return wrapper


@observe(as_type="generation")
def send_completion(
    model_name,
    messages,
    functions,
    stream,
    temperature=0,
    extra_params=None,
):
    from aider.llm import litellm

    kwargs = dict(
        model=model_name,
        messages=messages,
        stream=stream,
    )
    if temperature is not None:
        kwargs["temperature"] = temperature

    if functions is not None:
        function = functions[0]
        kwargs["tools"] = [dict(type="function", function=function)]
        kwargs["tool_choice"] = {"type": "function", "function": {"name": function["name"]}}

    if extra_params is not None:
        kwargs.update(extra_params)

    key = json.dumps(kwargs, sort_keys=True).encode()

    # Generate SHA1 hash of kwargs and append it to chat_completion_call_hashes
    hash_object = hashlib.sha1(key)

    if not stream and CACHE is not None and key in CACHE:
        return hash_object, CACHE[key]

    # Update Langfuse tracing context before LLM call
    langfuse_context.update_current_observation(
        input={
            'model_name': model_name,
            'messages': messages,
            'functions': functions,
            'stream': stream,
            'temperature': temperature,
            'extra_params': extra_params,
        },
        model=model_name,
    )

    res = litellm.completion(**kwargs)

    # Update Langfuse tracing context after LLM call
    langfuse_context.update_current_observation(
        output=res.choices,
        usage={
            'input': res.usage.prompt_tokens,
            'output': res.usage.completion_tokens,
        },
    )

    if not stream and CACHE is not None:
        CACHE[key] = res

    return hash_object, res


@lazy_litellm_retry_decorator
def simple_send_with_retries(model_name, messages, extra_params=None):
    try:
        kwargs = {
            "model_name": model_name,
            "messages": messages,
            "functions": None,
            "stream": False,
            "extra_params": extra_params,
        }

        _hash, response = send_completion(**kwargs)
        return response.choices[0].message.content
    except (AttributeError, litellm.exceptions.BadRequestError):
        return
