import hashlib
import json

import backoff
from langfuse.decorators import observe
from llm_multiple_choice import DisplayFormat

from aider.llm import litellm


def is_anthropic_model(model_name):
    """
    Determine if a model is an Anthropic model by checking:
    - If it contains 'claude' in its name

    Args:
        model_name (str): The name of the model to check

    Returns:
        bool: True if the model is an Anthropic model, False otherwise
    """
    if not model_name:
        return False

    model_name = model_name.lower()

    # Check if it's just a claude model
    if "claude" in model_name:
        return True

    return False


def transform_messages_for_anthropic(messages):
    """
    Transform message sequences for Anthropic models according to these rules:
    - Concatenate all system messages into one opening system message.
    - Ensure there's a user message after the system message.
    - Separate consecutive user messages with assistant messages saying "Understood."
    - Separate consecutive assistant messages with user messages saying "Please continue."
    """
    result = []

    # Combine system messages if present
    system_messages = [msg for msg in messages if msg["role"] == "system"]
    other_messages = [msg for msg in messages if msg["role"] != "system"]

    if system_messages:
        # Handle the case where content might be a list (for image messages)
        combined_content = []
        for msg in system_messages:
            content = msg["content"]
            if isinstance(content, list):
                # For messages containing images, extract text portions
                text_parts = [
                    item["text"] for item in content if isinstance(item, dict) and "text" in item
                ]
                combined_content.extend(text_parts)
            else:
                combined_content.append(content)

        combined_system = {"role": "system", "content": "\n\n".join(combined_content)}
        result.append(combined_system)

    # If no user message follows system, add "Go ahead."
    if not other_messages or other_messages[0]["role"] != "user":
        result.append({"role": "user", "content": "Go ahead."})

    last_role = result[-1]["role"] if result else None
    for msg in other_messages:
        # If two user messages would be consecutive
        if msg["role"] == "user" and last_role == "user":
            result.append({"role": "assistant", "content": "Understood."})
        # If two assistant messages would be consecutive
        elif msg["role"] == "assistant" and last_role == "assistant":
            result.append({"role": "user", "content": "Understood."})

        if isinstance(msg["content"], list):
            # For messages containing images, extract and join text portions
            text_parts = [
                item["text"] for item in msg["content"] if isinstance(item, dict) and "text" in item
            ]
            msg = dict(msg)  # Make a copy to avoid modifying the original
            msg["content"] = " ".join(text_parts) if text_parts else ""

        result.append(msg)
        last_role = msg["role"]

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
    if is_anthropic_model(model_name):
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


@observe(name="llm-completion", as_type="generation")
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


@observe
def analyze_assistant_response(
    choice_manager,
    introduction,
    model_name,
    response_text,
    extra_params=None,
):
    """
    Analyze an assistant's response using a multiple choice questionnaire.

    This function analyzes a single response string using a questionnaire. It's a more
    focused version of analyze_chat_situation that takes just the response text rather
    than the full chat context.

    Args:
        choice_manager (ChoiceManager): The choice manager containing the questionnaire
        introduction (str): An introduction to the questionnaire explaining the context and goal.
            Write this as though for a human who will fill out the questionnaire. Refer to the
            assistant's response as appearing "below" -- it will automatically be appended
            at the end of the prompt, in a markdown section titled "Assistant's Response".
        model_name (str): The name of the language model to use
        response_text (str): The assistant's response text to analyze
        extra_params (dict, optional): Additional parameters to pass to the model.

    Returns:
        ChoiceCodeSet: The validated set of choices made by the model

    Raises:
        InvalidChoicesResponseError: If the model's response cannot be validated
    """
    prompt = choice_manager.prompt_for_choices(DisplayFormat.MARKDOWN, introduction)
    prompt += "\n\n# Assistant's Response\n\n" + response_text
    chat_messages = [{"role": "user", "content": prompt}]
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
        return
