import hashlib
import json
import logging

import backoff
from langfuse.decorators import langfuse_context, observe
from llm_multiple_choice import DisplayFormat, InvalidChoicesResponseError

from aider.exceptions import InvalidResponseError, SendCompletionError
from aider.llm import litellm

logger = logging.getLogger(__name__)


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
        InvalidResponseError,
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
    purpose="send-completion",
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
            - hash_object (hashlib.sha1): A SHA1 hash object of the request parameters
            - res: The model's response object. The structure depends on stream mode:
                When stream=False:
                    - choices[0].message.content: The complete response text
                    - choices[0].tool_calls[0].function: Function call details if tools were used
                    - usage.prompt_tokens: Number of input tokens
                    - usage.completion_tokens: Number of output tokens
                    - usage.total_cost: Total cost in USD if available
                    - usage.prompt_cost: Input cost in USD if available
                    - usage.completion_cost: Output cost in USD if available
                When stream=True:
                    Returns an iterator yielding chunks, where each chunk has:
                    - choices[0].delta.content: The next piece of response text
                    - choices[0].delta.tool_calls[0].function: Partial function call details
                    - usage: Only available in final chunk if stream_options.include_usage=True

    Raises:
        SendCompletionError: If the API returns a non-200 status code
        InvalidResponseError: If the response is missing required fields or empty
        litellm.exceptions.RateLimitError: If rate limit is exceeded
        litellm.exceptions.APIError: For various API-level errors
        litellm.exceptions.Timeout: If the request times out
        litellm.exceptions.APIConnectionError: For network connectivity issues
        litellm.exceptions.ServiceUnavailableError: If the service is unavailable
        litellm.exceptions.InternalServerError: For server-side errors
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
        kwargs["tool_choice"] = {
            "type": "function",
            "function": {"name": function["name"]},
        }

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
        purpose=purpose,
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
    purpose="(unlabeled)",
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
        purpose (str, optional): The purpose of this completion, used as the name in Langfuse.
                               Defaults to "llm-completion".

    Returns:
        res: The model's response object. The structure depends on stream mode:
            When stream=False:
                - choices[0].message.content: The complete response text
                - choices[0].tool_calls[0].function: Function call details if tools were used
                - usage.prompt_tokens: Number of input tokens
                - usage.completion_tokens: Number of output tokens
                - usage.total_cost: Total cost in USD if available
                - usage.prompt_cost: Input cost in USD if available
                - usage.completion_cost: Output cost in USD if available
            When stream=True:
                Returns an iterator yielding chunks, where each chunk has:
                - choices[0].delta.content: The next piece of response text
                - choices[0].delta.tool_calls[0].function: Partial function call details
                - usage: Not available
                  (We could change our implementation to add this
                  by setting stream_options.include_usage=True)

    Raises:
        SendCompletionError: If the API returns a non-200 status code
        InvalidResponseError: If the response is missing required fields or empty
        litellm.exceptions.RateLimitError: If rate limit is exceeded
        litellm.exceptions.APIError: For various API-level errors
        litellm.exceptions.Timeout: If the request times out
        litellm.exceptions.APIConnectionError: For network connectivity issues
        litellm.exceptions.ServiceUnavailableError: If the service is unavailable
        litellm.exceptions.InternalServerError: For server-side errors

    Notes:
        - This function uses Langfuse for tracing and monitoring.
        - The `@observe` decorator captures input and output for Langfuse.
        - Usage information is captured in Langfuse for both streaming and non-streaming responses.
    """
    # Use the provided purpose as the name in Langfuse trace
    langfuse_context.update_current_observation(name=purpose, model=model_name, input=messages)

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
        kwargs["tool_choice"] = {
            "type": "function",
            "function": {"name": function["name"]},
        }

    if extra_params is not None:
        kwargs.update(extra_params)

    try:
        res = litellm.completion(**kwargs)
    except (litellm.exceptions.RateLimitError, litellm.exceptions.APIError) as e:
        # Log the error before re-raising for retry
        logger.warning(f"LiteLLM error ({type(e).__name__}): {str(e)}")
        # Re-raise these exceptions to be handled by the retry decorator
        raise

    # Handle None response
    if res is None:
        error_message = f"Received None response from {model_name}"
        logger.error(error_message)
        raise InvalidResponseError(error_message)

    # Check for non-200 status code first
    if hasattr(res, "status_code") and res.status_code != 200:
        error_message = f"Error sending completion to {model_name}: {res.status_code} - {res.text}"
        raise SendCompletionError(error_message, status_code=res.status_code)

    usage = None
    if hasattr(res, "usage"):
        usage = {
            "input": res.usage.prompt_tokens,
            "output": res.usage.completion_tokens,
            "unit": "TOKENS",
        }

        # Add cost information if available
        if hasattr(res.usage, "total_cost"):
            usage["total_cost"] = res.usage.total_cost
        elif hasattr(res.usage, "completion_cost") and hasattr(res.usage, "prompt_cost"):
            usage["input_cost"] = res.usage.prompt_cost
            usage["output_cost"] = res.usage.completion_cost

    if stream:
        langfuse_context.update_current_observation(usage=usage, name=purpose)
    else:
        # Handle case where response has text but no choices
        if not hasattr(res, "choices"):
            error_message = f"Response from {model_name} has no choices attribute"
            logger.error(error_message + "\nResponse: " + str(res))
            raise InvalidResponseError(error_message)

        # Handle empty choices list
        if len(res.choices) == 0:
            error_message = f"Received empty choices list from {model_name}"
            logger.error(error_message + "\nResponse: " + str(res))
            raise InvalidResponseError(error_message)

        output = None
        choice = res.choices[0]

        # Handle function calls
        if hasattr(choice, "tool_calls") and choice.tool_calls:
            tool_call = choice.tool_calls[0]
            if hasattr(tool_call, "function"):
                output = tool_call.function

        # Handle regular content
        if hasattr(choice, "message") and hasattr(choice.message, "content"):
            output = choice.message.content

        langfuse_context.update_current_observation(
            name=purpose,
            input=str(messages),  # Convert messages to string for logging
            output=output if output else None,
            model=model_name,
            usage=usage if usage else None,
        )

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
        purpose="analyze chat",
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
        InvalidChoicesResponseError: If the model's response cannot be validated even after retries
    """
    max_retries = 3
    previous_response = None
    previous_error = None

    for attempt in range(max_retries):
        prompt = choice_manager.prompt_for_choices(DisplayFormat.MARKDOWN, introduction)
        if attempt > 0:
            # Include previous error in retry attempts
            prompt += "\n\n# Previous Error\n\n"
            prompt += f"You previously responded with this: {previous_response}\n\n"
            prompt += (
                f"That response gave the following error:\n{previous_error}\n\nPlease try again."
            )

        prompt += "\n\n# Assistant's Response\n\n" + response_text

        chat_messages = [{"role": "user", "content": prompt}]
        _hash, response = send_completion(
            model_name=model_name,
            messages=chat_messages,
            functions=None,
            stream=False,
            temperature=0,
            extra_params=extra_params,
            purpose=f"analyze assistant response (attempt {attempt + 1})",
        )
        content = response.choices[0].message.content

        try:
            return choice_manager.validate_choices_response(content)
        except InvalidChoicesResponseError as e:
            previous_response = content
            previous_error = str(e)
            if attempt == max_retries - 1:  # Last attempt
                raise  # Re-raise the last error if all retries failed
            logger.warning(f"Invalid choices response (attempt {attempt + 1}): {previous_error}")


@lazy_litellm_retry_decorator
def simple_send_with_retries(model_name, messages, extra_params=None, purpose="send with retries"):
    """
    Send a completion request with retries on various error conditions.

    This function wraps send_completion with retry logic for handling various error types.
    It will retry on connection errors, rate limit errors, and invalid responses.

    Args:
        model_name (str): The name of the language model to use
        messages (list): A list of message dictionaries to send to the model
        extra_params (dict, optional): Additional parameters to pass to the model
        purpose (str, optional): The purpose label for this completion request for Langfuse tracing

    Returns:
        str: The content of the model's response

    Raises:
        SendCompletionError: If the request fails with a non-200 status code
        InvalidResponseError: If the response is missing required fields or empty
    """
    kwargs = {
        "model_name": model_name,
        "messages": messages,
        "functions": None,
        "stream": False,
        "extra_params": extra_params,
        "purpose": purpose,
    }

    _hash, response = send_completion(**kwargs)

    # Extract content from response
    if hasattr(response, "choices") and response.choices:
        return response.choices[0].message.content
    else:
        error_message = f"Invalid response from {model_name}: missing choices"
        logger.error(error_message)
        raise InvalidResponseError(error_message)
