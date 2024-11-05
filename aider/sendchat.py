import hashlib
import json

import backoff
from langfuse.decorators import observe
from llm_multiple_choice import DisplayFormat

from aider.llm import litellm

def transform_messages_for_anthropic(messages):
    """
    Transform message sequences for Anthropic models according to their requirements:
    - First system message must be at the start
    - No system messages allowed after user/assistant messages
    - No multiple consecutive system messages
    """
    # Find first system message if any
    system_messages = [msg for msg in messages if msg["role"] == "system"]
    other_messages = [msg for msg in messages if msg["role"] != "system"]
    
    if not system_messages:
        return messages

    # Take first system message, discard others
    result = [system_messages[0]] + other_messages
    return result

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


def send_completion(
    model_name,
    messages,
    functions,
    stream,
    temperature=0,
    extra_params=None,
):
    """
    Send a completion request to the language model and handle the response.

    This function manages caching of responses when applicable and delegates the actual LLM
    call to `_send_completion_to_litellm`. It adapts its behavior based on whether streaming
    is enabled or not.

    Args:
        model_name (str): The name of the language model to use.
        messages (list): A list of message dictionaries to send to the model.
        functions (list): A list of function definitions that the model can use.
        stream (bool): Whether to stream the response or not.
        temperature (float, optional): The sampling temperature to use. Defaults to 0.
        extra_params (dict, optional): Additional parameters to pass to the model. Defaults to None.

    Returns:
        tuple: A tuple containing:
            - hash_object (hashlib.sha1): A SHA1 hash object of the request parameters.
            - res: The model's response object.

    """
    # Transform messages for Anthropic models
    if model_name.startswith(("anthropic.", "claude")):
        messages = transform_messages_for_anthropic(messages)
        
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

    # Generate SHA1 hash of kwargs to use as a cache key
    hash_object = hashlib.sha1(key)

    if not stream and CACHE is not None and key in CACHE:
        return hash_object, CACHE[key]

    # Call the actual LLM function
    res = _send_completion_to_litellm(
        model_name=model_name,
        messages=messages,
        functions=functions,
        stream=stream,
        temperature=temperature,
        extra_params=extra_params,
    )

    if not stream and CACHE is not None:
        CACHE[key] = res

    return hash_object, res


@observe(as_type="generation")
def _send_completion_to_litellm(
    model_name,
    messages,
    functions,
    stream,
    temperature=0,
    extra_params=None,
):
    """
    Sends the completion request to litellm.completion and handles the response.

    This function sends a request to the specified language model and returns the response.
    It supports both streaming and non-streaming responses.

    Args:
        model_name (str): The name of the language model to use.
        messages (list): A list of message dictionaries to send to the model.
        functions (list): A list of function definitions that the model can use.
        stream (bool): Whether to stream the response or not.
        temperature (float, optional): The sampling temperature to use. Defaults to 0.
        extra_params (dict, optional): Additional parameters to pass to the model. Defaults to None.

    Returns:
        res: The model's response object.

    Notes:
        - This function uses Langfuse for tracing and monitoring.
        - It adapts its behavior based on whether streaming is enabled or not.
        - The `@observe` decorator captures input and output for Langfuse.
    """
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

    res = litellm.completion(**kwargs)

    return res


@observe
def analyze_chat_situation(
    choice_manager,
    introduction,
    model_name,
    messages,
    extra_params=None,
):
    """
    Analyze the current chat situation using a multiple choice questionnaire.

    This function sends the chat context to the model and has it fill out a questionnaire
    about the current situation. It uses the same underlying send_completion mechanism
    as other chat functions, but adds validation of the response against the provided
    choice manager.

    Args:
        choice_manager (ChoiceManager): The choice manager containing the questionnaire
        introduction (str): An introduction to the questionnaire explaining the context and goal,
            written as though a human would fill out the questionnaire.
        model_name (str): The name of the language model to use
        messages (list): A list of message dictionaries to send to the model
        extra_params (dict, optional): Additional parameters to pass to the model.

    Returns:
        ChoiceCodeSet: The validated set of choices made by the model

    Raises:
        InvalidChoicesResponseError: If the model's response cannot be validated
    """
    prompt = choice_manager.prompt_for_choices(DisplayFormat.MARKDOWN, introduction)
    chat_messages = messages + [{"role": "user", "content": prompt}]
    _hash, response = send_completion(
        model_name=model_name,
        messages=chat_messages,
        functions=None,
        stream=False,
        temperature=0,
        extra_params=extra_params,
    )
    content = response.choices[0].message.content
    return choice_manager.validate_choices_response(content)


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
