Log in [Sign up](https://platform.openai.com/signup)

## Introduction

You can interact with the API through HTTP requests from any language, via our official Python bindings, our official Node.js library, or a [community-maintained library](https://platform.openai.com/docs/libraries#community-libraries).

To install the official Python bindings, run the following command:

```bash
pip install openai
```

To install the official Node.js library, run the following command in your Node.js project directory:

```bash
npm install openai
```

## Authentication

### API keys

The OpenAI API uses API keys for authentication. You can create API keys at a user or service account level. Service accounts are tied to a "bot" individual and should be used to provision access for production systems. Each API key can be scoped to one of the following,

1. **Project keys** \- Provides access to a single project ( **preferred option**); access [Project API keys](https://platform.openai.com/settings/organization/general) by selecting the specific project you wish to generate keys against.
2. **User keys** \- Our legacy keys. Provides access to all organizations and all projects that user has been added to; access [API Keys](https://platform.openai.com/settings/organization/api-keys) to view your available keys. We highly advise transitioning to project keys for best security practices, although access via this method is currently still supported.

**Remember that your API key is a secret!** Do not share it with others or expose it in any client-side code (browsers, apps). Production requests must be routed through your own backend server where your API key can be securely loaded from an environment variable or key management service.

All API requests should include your API key in an `Authorization` HTTP header as follows:

```bash
Authorization: Bearer OPENAI_API_KEY
```

### Organizations and projects (optional)

For users who belong to multiple organizations or are accessing their projects through their legacy user API key, you can pass a header to specify which organization and project is used for an API request. Usage from these API requests will count as usage for the specified organization and project.

Example curl command:

```bash
1
2
3
4
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Organization: YOUR_ORG_ID" \
  -H "OpenAI-Project: $PROJECT_ID"
```

Example with the `openai` Python package:

```python
1
2
3
4
5
6
from openai import OpenAI

client = OpenAI(
  organization='YOUR_ORG_ID',
  project='$PROJECT_ID',
)
```

Example with the `openai` Node.js package:

```javascript
1
2
3
4
5
6
import OpenAI from "openai";

const openai = new OpenAI({
    organization: "YOUR_ORG_ID",
    project: "$PROJECT_ID",
});
```

Organization IDs can be found on your [Organization settings](https://platform.openai.com/settings/organization/general) page.
Project IDs can be found on your [General settings](https://platform.openai.com/settings) page by selecting the specific project.

## Making requests

You can paste the command below into your terminal to run your first API request. Make sure to replace `$OPENAI_API_KEY` with your secret API key. If you are using a legacy user key and you have multiple projects, you will also need to [specify the Project Id](https://platform.openai.com/docs/api-reference/authentication). For improved security, we recommend transitioning to project based keys instead.

```bash
1
2
3
4
5
6
7
8
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
     "model": "gpt-4o-mini",
     "messages": [{"role": "user", "content": "Say this is a test!"}],
     "temperature": 0.7
   }'
```

This request queries the `gpt-4o-mini` model (which under the hood points to a [`gpt-4o-mini` model variant](https://platform.openai.com/docs/models#gpt-4o-mini)) to complete the text starting with a prompt of " _Say this is a test_". You should get a response back that resembles the following:

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
{
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "created": 1677858242,
    "model": "gpt-4o-mini",
    "usage": {
        "prompt_tokens": 13,
        "completion_tokens": 7,
        "total_tokens": 20,
        "completion_tokens_details": {
            "reasoning_tokens": 0,
            "accepted_prediction_tokens": 0,
            "rejected_prediction_tokens": 0
        }
    },
    "choices": [\
        {\
            "message": {\
                "role": "assistant",\
                "content": "\n\nThis is a test!"\
            },\
            "logprobs": null,\
            "finish_reason": "stop",\
            "index": 0\
        }\
    ]
}
```

Now that you've generated your first chat completion, let's break down the [response object](https://platform.openai.com/docs/api-reference/chat/object). We can see the `finish_reason` is `stop` which means the API returned the full chat completion generated by the model without running into any limits. In the choices list, we only generated a single message but you can set the `n` parameter to generate multiple messages choices.

## Streaming

The OpenAI API provides the ability to stream responses back to a client in order to allow partial results for certain requests. To achieve this, we follow the [Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events) standard. Our official [Node](https://github.com/openai/openai-node?tab=readme-ov-file#streaming-responses) and [Python](https://github.com/openai/openai-python?tab=readme-ov-file#streaming-responses) libraries include helpers to make parsing these events simpler.

Streaming is supported for both the [Chat Completions API](https://platform.openai.com/docs/api-reference/chat/streaming) and the [Assistants API](https://platform.openai.com/docs/api-reference/runs/createRun). This section focuses on how streaming works for Chat Completions. Learn more about how streaming works in the Assistants API [here](https://platform.openai.com/docs/assistants/overview).

In Python, a streaming request looks like:

```python
1
2
3
4
5
6
7
8
9
10
11
12
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

In Node / Typescript, a streaming request looks like:

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
    const stream = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [{ role: "user", content: "Say this is a test" }],
        store: true,
        stream: true,
    });
    for await (const chunk of stream) {
        process.stdout.write(chunk.choices[0]?.delta?.content || "");
    }
}

main();
```

#### Parsing Server-sent events

Parsing Server-sent events is non-trivial and should be done with caution. Simple strategies like splitting by a new line may result in parsing errors. We recommend using [existing client libraries](https://platform.openai.com/docs/libraries) when possible.

## Debugging requests

In addition to [error codes](https://platform.openai.com/docs/guides/error-codes) returned from API responses, it may sometimes be necessary to inspect HTTP response headers as well. Of particular interest will be the headers which contain the unique ID of a particular API request, and information about rate limiting applied to your requests. Below is an incomplete list of HTTP headers returned with API responses:

**API meta information**

- `openai-organization`: The [organization](https://platform.openai.com/docs/guides/production-best-practices#setting-up-your-organization) associated with the request
- `openai-processing-ms`: Time taken processing your API request
- `openai-version`: REST API version used for this request (currently `2020-10-01`)
- `x-request-id`: Unique identifier for this API request (used in troubleshooting)

**[Rate limiting information](https://platform.openai.com/docs/guides/rate-limits)**

- `x-ratelimit-limit-requests`
- `x-ratelimit-limit-tokens`
- `x-ratelimit-remaining-requests`
- `x-ratelimit-remaining-tokens`
- `x-ratelimit-reset-requests`
- `x-ratelimit-reset-tokens`

**OpenAI recommends logging request IDs in production deployments**, which will allow more efficient troubleshooting with our [support team](https://help.openai.com/en/) should the need arise. Our official SDKs provide a property on top level response objects containing the value of the `x-request-id` header.

**Request ID in Python**

```python
1
2
3
4
5
6
7
8
9
10
11
12
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    messages=[{\
        "role": "user",\
        "content": "Say this is a test",\
    }],
    model="gpt-4o-mini",
)

print(response._request_id)
```

**Request ID in JavaScript**

```javascript
1
2
3
4
5
6
7
8
9
import OpenAI from 'openai';
const client = new OpenAI();

const response = await client.chat.completions.create({
    messages: [{ role: 'user', content: 'Say this is a test' }],
    model: 'gpt-4o-mini'
});

console.log(response._request_id);
```

### Access raw response objects in SDKs

If you are using a lower-level HTTP client (like [fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) or [`HttpClient` in C#](https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/http/httpclient)), you should already have access to response headers as a part of the HTTP interface.

If you are using one of OpenAI's [official SDKs](https://platform.openai.com/docs/libraries) (which largely abstract the HTTP request/response cycle), you will need to access raw HTTP responses in a slightly different way.

Below is an example of accessing the raw response object (and the `x-ratelimit-limit-tokens` header) using our [Python SDK](https://github.com/openai/openai-python?tab=readme-ov-file#accessing-raw-response-data-eg-headers).

```python
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.with_raw_response.create(
    messages=[{\
        "role": "user",\
        "content": "Say this is a test",\
    }],
    model="gpt-4o-mini",
)
print(response.headers.get('x-ratelimit-limit-tokens'))

# get the object that `chat.completions.create()` would have returned
completion = response.parse()
print(completion)
```

Here is how you'd access a raw response (and the `x-ratelimit-limit-tokens` header) using our [JavaScript SDK](https://github.com/openai/openai-node?tab=readme-ov-file#accessing-raw-response-data-eg-headers).

```javascript
1
2
3
4
5
6
7
8
9
10
import OpenAI from 'openai';
const client = new OpenAI();

const response = await client.chat.completions.create({
    messages: [{ role: 'user', content: 'Say this is a test' }],
    model: 'gpt-4o-mini'
}).asResponse();

// access the underlying Response object
console.log(response.headers.get('x-ratelimit-limit-tokens'));
```

## Backward compatibility

OpenAI is committed to providing stability to API users by avoiding breaking changes in major API versions whenever reasonably possible. This includes:

- The REST API (currently `v1`)
- Our first-party [SDKs](https://platform.openai.com/docs/libraries) (released SDKs will adhere to [semantic versioning](https://semver.org/))
- [Model](https://platform.openai.com/docs/models) families (like `gpt-4o` or `o1-mini`)

Backwards-compatible changes and upgrades will be continuously delivered over time. These and any rare breaking changes will be communicated in the [changelog](https://platform.openai.com/docs/changelog). Here are some examples of changes which we consider to be backwards-compatible (non-breaking) changes.

**Changes in model prompting behavior between snapshots**

Model outputs are by their nature variable, so changes in prompting and model behavior between snapshots should be expected. For example, if you moved from `gpt-4o-2024-05-13` to `gpt-4o-2024-08-06`, the same `system` or `user` messages could function differently between versions. The best way to ensure consistent prompting behavior and model output is to use pinned model versions, and to implement [evals](https://platform.openai.com/docs/guides/evals) for your applications.

**Backwards-compatible API changes**

- Adding new resources (URLs) to the REST API and SDKs
- Adding new optional API parameters
- Adding new properties to JSON response objects or event data
- Changing the order of properties in a JSON response object
- Changing the length or format of opaque strings, like resource identifiers and UUIDs
- Adding new event types (in either streaming or the Realtime API)

## Audio

Learn how to turn audio into text or text into audio.

Related guide: [Speech to text](https://platform.openai.com/docs/guides/speech-to-text)

## Create speech

posthttps://api.openai.com/v1/audio/speech

Generates audio from the input text.

### Request body

model

string

Required

One of the available [TTS models](https://platform.openai.com/docs/models#tts): `tts-1` or `tts-1-hd`

input

string

Required

The text to generate audio for. The maximum length is 4096 characters.

voice

string

Required

The voice to use when generating the audio. Supported voices are `alloy`, `ash`, `coral`, `echo`, `fable`, `onyx`, `nova`, `sage` and `shimmer`. Previews of the voices are available in the [Text to speech guide](https://platform.openai.com/docs/guides/text-to-speech#voice-options).

response\_format

string

Optional

Defaults to mp3

The format to audio in. Supported formats are `mp3`, `opus`, `aac`, `flac`, `wav`, and `pcm`.

speed

number

Optional

Defaults to 1

The speed of the generated audio. Select a value from `0.25` to `4.0`. `1.0` is the default.

### Returns

The audio file content.

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "The quick brown fox jumped over the lazy dog.",
    "voice": "alloy"
  }' \
  --output speech.mp3
```

```python
1
2
3
4
5
6
7
8
9
10
from pathlib import Path
import openai

speech_file_path = Path(__file__).parent / "speech.mp3"
response = openai.audio.speech.create(
  model="tts-1",
  voice="alloy",
  input="The quick brown fox jumped over the lazy dog."
)
response.stream_to_file(speech_file_path)
```

```node
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
import fs from "fs";
import path from "path";
import OpenAI from "openai";

const openai = new OpenAI();

const speechFile = path.resolve("./speech.mp3");

async function main() {
  const mp3 = await openai.audio.speech.create({
    model: "tts-1",
    voice: "alloy",
    input: "Today is a wonderful day to build something people love!",
  });
  console.log(speechFile);
  const buffer = Buffer.from(await mp3.arrayBuffer());
  await fs.promises.writeFile(speechFile, buffer);
}
main();
```

## Create transcription

posthttps://api.openai.com/v1/audio/transcriptions

Transcribes audio into the input language.

### Request body

file

file

Required

The audio file object (not file name) to transcribe, in one of these formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.

model

string

Required

ID of the model to use. Only `whisper-1` (which is powered by our open source Whisper V2 model) is currently available.

language

string

Optional

The language of the input audio. Supplying the input language in [ISO-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (e.g. `en`) format will improve accuracy and latency.

prompt

string

Optional

An optional text to guide the model's style or continue a previous audio segment. The [prompt](https://platform.openai.com/docs/guides/speech-to-text#prompting) should match the audio language.

response\_format

string

Optional

Defaults to json

The format of the output, in one of these options: `json`, `text`, `srt`, `verbose_json`, or `vtt`.

temperature

number

Optional

Defaults to 0

The sampling temperature, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. If set to 0, the model will use [log probability](https://en.wikipedia.org/wiki/Log_probability) to automatically increase the temperature until certain thresholds are hit.

timestamp\_granularities\[\]

array

Optional

Defaults to segment

The timestamp granularities to populate for this transcription. `response_format` must be set `verbose_json` to use timestamp granularities. Either or both of these options are supported: `word`, or `segment`. Note: There is no additional latency for segment timestamps, but generating word timestamps incurs additional latency.

### Returns

The [transcription object](https://platform.openai.com/docs/api-reference/audio/json-object) or a [verbose transcription object](https://platform.openai.com/docs/api-reference/audio/verbose-json-object).

DefaultDefaultWord timestampsWord timestampsSegment timestampsSegment timestamps

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@/path/to/file/audio.mp3" \
  -F model="whisper-1"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

audio_file = open("speech.mp3", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper-1",
  file=audio_file
)
```

```node
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import fs from "fs";
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const transcription = await openai.audio.transcriptions.create({
    file: fs.createReadStream("audio.mp3"),
    model: "whisper-1",
  });

  console.log(transcription.text);
}
main();
```

Response

```json
1
2
3
{
  "text": "Imagine the wildest idea that you've ever had, and you're curious about how it might scale to something that's a 100, a 1,000 times bigger. This is a place where you can get to do that."
}
```

## Create translation

posthttps://api.openai.com/v1/audio/translations

Translates audio into English.

### Request body

file

file

Required

The audio file object (not file name) translate, in one of these formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.

model

string

Required

ID of the model to use. Only `whisper-1` (which is powered by our open source Whisper V2 model) is currently available.

prompt

string

Optional

An optional text to guide the model's style or continue a previous audio segment. The [prompt](https://platform.openai.com/docs/guides/speech-to-text#prompting) should be in English.

response\_format

string

Optional

Defaults to json

The format of the output, in one of these options: `json`, `text`, `srt`, `verbose_json`, or `vtt`.

temperature

number

Optional

Defaults to 0

The sampling temperature, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. If set to 0, the model will use [log probability](https://en.wikipedia.org/wiki/Log_probability) to automatically increase the temperature until certain thresholds are hit.

### Returns

The translated text.

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/audio/translations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@/path/to/file/german.m4a" \
  -F model="whisper-1"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

audio_file = open("speech.mp3", "rb")
transcript = client.audio.translations.create(
  model="whisper-1",
  file=audio_file
)
```

```node
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import fs from "fs";
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
    const translation = await openai.audio.translations.create({
        file: fs.createReadStream("speech.mp3"),
        model: "whisper-1",
    });

    console.log(translation.text);
}
main();
```

Response

```json
1
2
3
{
  "text": "Hello, my name is Wolfgang and I come from Germany. Where are you heading today?"
}
```

## The transcription object (JSON)

Represents a transcription response returned by model, based on the provided input.

text

string

The transcribed text.

OBJECT The transcription object (JSON)

```JSON
1
2
3
{
  "text": "Imagine the wildest idea that you've ever had, and you're curious about how it might scale to something that's a 100, a 1,000 times bigger. This is a place where you can get to do that."
}
```

## The transcription object (Verbose JSON)

Represents a verbose json transcription response returned by model, based on the provided input.

language

string

The language of the input audio.

duration

string

The duration of the input audio.

text

string

The transcribed text.

words

array

Extracted words and their corresponding timestamps.

Show properties

segments

array

Segments of the transcribed text and their corresponding details.

Show properties

OBJECT The transcription object (Verbose JSON)

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
{
  "task": "transcribe",
  "language": "english",
  "duration": 8.470000267028809,
  "text": "The beach was a popular spot on a hot summer day. People were swimming in the ocean, building sandcastles, and playing beach volleyball.",
  "segments": [\
    {\
      "id": 0,\
      "seek": 0,\
      "start": 0.0,\
      "end": 3.319999933242798,\
      "text": " The beach was a popular spot on a hot summer day.",\
      "tokens": [\
        50364, 440, 7534, 390, 257, 3743, 4008, 322, 257, 2368, 4266, 786, 13, 50530\
      ],\
      "temperature": 0.0,\
      "avg_logprob": -0.2860786020755768,\
      "compression_ratio": 1.2363636493682861,\
      "no_speech_prob": 0.00985979475080967\
    },\
    ...\
  ]
}
```

## Chat

Given a list of messages comprising a conversation, the model will return a response.
Related guide: [Chat Completions](https://platform.openai.com/docs/guides/text-generation)

## Create chat completion

posthttps://api.openai.com/v1/chat/completions

Creates a model response for the given chat conversation. Learn more in the
[text generation](https://platform.openai.com/docs/guides/text-generation), [vision](https://platform.openai.com/docs/guides/vision),
and [audio](https://platform.openai.com/docs/guides/audio) guides.

Parameter support can differ depending on the model used to generate the
response, particularly for newer reasoning models. Parameters that are only
supported for reasoning models are noted below. For the current state of
unsupported parameters in reasoning models,
[refer to the reasoning guide](https://platform.openai.com/docs/guides/reasoning).

### Request body

messages

array

Required

A list of messages comprising the conversation so far. Depending on the
[model](https://platform.openai.com/docs/models) you use, different message types (modalities) are
supported, like [text](https://platform.openai.com/docs/guides/text-generation),
[images](https://platform.openai.com/docs/guides/vision), and [audio](https://platform.openai.com/docs/guides/audio).

Show possible types

model

string

Required

ID of the model to use. See the [model endpoint compatibility](https://platform.openai.com/docs/models#model-endpoint-compatibility) table for details on which models work with the Chat API.

store

boolean or null

Optional

Defaults to false

Whether or not to store the output of this chat completion request for
use in our [model distillation](https://platform.openai.com/docs/guides/distillation) or
[evals](https://platform.openai.com/docs/guides/evals) products.

reasoning\_effort

string

Optional

Defaults to medium

**o1 models only**

Constrains effort on reasoning for
[reasoning models](https://platform.openai.com/docs/guides/reasoning).
Currently supported values are `low`, `medium`, and `high`. Reducing
reasoning effort can result in faster responses and fewer tokens used
on reasoning in a response.

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

frequency\_penalty

number or null

Optional

Defaults to 0

Number between -2.0 and 2.0. Positive values penalize new tokens based on
their existing frequency in the text so far, decreasing the model's
likelihood to repeat the same line verbatim.

logit\_bias

map

Optional

Defaults to null

Modify the likelihood of specified tokens appearing in the completion.

Accepts a JSON object that maps tokens (specified by their token ID in the
tokenizer) to an associated bias value from -100 to 100. Mathematically,
the bias is added to the logits generated by the model prior to sampling.
The exact effect will vary per model, but values between -1 and 1 should
decrease or increase likelihood of selection; values like -100 or 100
should result in a ban or exclusive selection of the relevant token.

logprobs

boolean or null

Optional

Defaults to false

Whether to return log probabilities of the output tokens or not. If true,
returns the log probabilities of each output token returned in the
`content` of `message`.

top\_logprobs

integer or null

Optional

An integer between 0 and 20 specifying the number of most likely tokens to
return at each token position, each with an associated log probability.
`logprobs` must be set to `true` if this parameter is used.

max\_tokens

Deprecated

integer or null

Optional

The maximum number of [tokens](https://platform.openai.com/tokenizer) that can be generated in the
chat completion. This value can be used to control
[costs](https://openai.com/api/pricing/) for text generated via API.

This value is now deprecated in favor of `max_completion_tokens`, and is
not compatible with [o1 series models](https://platform.openai.com/docs/guides/reasoning).

max\_completion\_tokens

integer or null

Optional

An upper bound for the number of tokens that can be generated for a completion, including visible output tokens and [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

n

integer or null

Optional

Defaults to 1

How many chat completion choices to generate for each input message. Note that you will be charged based on the number of generated tokens across all of the choices. Keep `n` as `1` to minimize costs.

modalities

array or null

Optional

Output types that you would like the model to generate for this request.
Most models are capable of generating text, which is the default:

`["text"]`

The `gpt-4o-audio-preview` model can also be used to [generate audio](https://platform.openai.com/docs/guides/audio). To
request that this model generate both text and audio responses, you can
use:

`["text", "audio"]`

prediction

object

Optional

Configuration for a [Predicted Output](https://platform.openai.com/docs/guides/predicted-outputs),
which can greatly improve response times when large parts of the model
response are known ahead of time. This is most common when you are
regenerating a file with only minor changes to most of the content.

Show possible types

audio

object or null

Optional

Parameters for audio output. Required when audio output is requested with
`modalities: ["audio"]`. [Learn more](https://platform.openai.com/docs/guides/audio).

Show properties

presence\_penalty

number or null

Optional

Defaults to 0

Number between -2.0 and 2.0. Positive values penalize new tokens based on
whether they appear in the text so far, increasing the model's likelihood
to talk about new topics.

response\_format

object

Optional

An object specifying the format that the model must output.

Setting to `{ "type": "json_schema", "json_schema": {...} }` enables
Structured Outputs which ensures the model will match your supplied JSON
schema. Learn more in the [Structured Outputs\\
guide](https://platform.openai.com/docs/guides/structured-outputs).

Setting to `{ "type": "json_object" }` enables JSON mode, which ensures
the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model
to produce JSON yourself via a system or user message. Without this, the
model may generate an unending stream of whitespace until the generation
reaches the token limit, resulting in a long-running and seemingly "stuck"
request. Also note that the message content may be partially cut off if
`finish_reason="length"`, which indicates the generation exceeded
`max_tokens` or the conversation exceeded the max context length.

Show possible types

seed

integer or null

Optional

This feature is in Beta.
If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same `seed` and parameters should return the same result.
Determinism is not guaranteed, and you should refer to the `system_fingerprint` response parameter to monitor changes in the backend.

service\_tier

string or null

Optional

Defaults to auto

Specifies the latency tier to use for processing the request. This parameter is relevant for customers subscribed to the scale tier service:

- If set to 'auto', and the Project is Scale tier enabled, the system will utilize scale tier credits until they are exhausted.
- If set to 'auto', and the Project is not Scale tier enabled, the request will be processed using the default service tier with a lower uptime SLA and no latency guarantee.
- If set to 'default', the request will be processed using the default service tier with a lower uptime SLA and no latency guarantee.
- When not set, the default behavior is 'auto'.

stop

string / array / null

Optional

Defaults to null

Up to 4 sequences where the API will stop generating further tokens.

stream

boolean or null

Optional

Defaults to false

If set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format) as they become available, with the stream terminated by a `data: [DONE]` message. [Example Python code](https://cookbook.openai.com/examples/how_to_stream_completions).

stream\_options

object or null

Optional

Defaults to null

Options for streaming response. Only set this when you set `stream: true`.

Show properties

temperature

number or null

Optional

Defaults to 1

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
We generally recommend altering this or `top_p` but not both.

top\_p

number or null

Optional

Defaults to 1

An alternative to sampling with temperature, called nucleus sampling,
where the model considers the results of the tokens with top\_p probability
mass. So 0.1 means only the tokens comprising the top 10% probability mass
are considered.

We generally recommend altering this or `temperature` but not both.

tools

array

Optional

A list of tools the model may call. Currently, only functions are supported as a tool. Use this to provide a list of functions the model may generate JSON inputs for. A max of 128 functions are supported.

Show properties

tool\_choice

string or object

Optional

Controls which (if any) tool is called by the model.
`none` means the model will not call any tool and instead generates a message.
`auto` means the model can pick between generating a message or calling one or more tools.
`required` means the model must call one or more tools.
Specifying a particular tool via `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool.

`none` is the default when no tools are present. `auto` is the default if tools are present.

Show possible types

parallel\_tool\_calls

boolean

Optional

Defaults to true

Whether to enable [parallel function calling](https://platform.openai.com/docs/guides/function-calling#configuring-parallel-function-calling) during tool use.

user

string

Optional

A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

function\_call

Deprecated

string or object

Optional

Deprecated in favor of `tool_choice`.

Controls which (if any) function is called by the model.

`none` means the model will not call a function and instead generates a
message.

`auto` means the model can pick between generating a message or calling a
function.

Specifying a particular function via `{"name": "my_function"}` forces the
model to call that function.

`none` is the default when no functions are present. `auto` is the default
if functions are present.

Show possible types

functions

Deprecated

array

Optional

Deprecated in favor of `tools`.

A list of functions the model may generate JSON inputs for.

Show properties

### Returns

Returns a [chat completion](https://platform.openai.com/docs/api-reference/chat/object) object, or a streamed sequence of [chat completion chunk](https://platform.openai.com/docs/api-reference/chat/streaming) objects if the request is streamed.

DefaultDefaultImage inputImage inputStreamingStreamingFunctionsFunctionsLogprobsLogprobs

Example request

gpt-4o

curl

```bash
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [\
      {\
        "role": "developer",\
        "content": "You are a helpful assistant."\
      },\
      {\
        "role": "user",\
        "content": "Hello!"\
      }\
    ]
  }'
```

```python
1
2
3
4
5
6
7
8
9
10
11
12
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-4o",
  messages=[\
    {"role": "developer", "content": "You are a helpful assistant."},\
    {"role": "user", "content": "Hello!"}\
  ]
)

print(completion.choices[0].message)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const completion = await openai.chat.completions.create({
    messages: [{ role: "developer", content: "You are a helpful assistant." }],
    model: "gpt-4o",
    store: true,
  });

  console.log(completion.choices[0]);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-4o-mini",
  "system_fingerprint": "fp_44709d6fcb",
  "choices": [{\
    "index": 0,\
    "message": {\
      "role": "assistant",\
      "content": "\n\nHello there, how may I assist you today?",\
    },\
    "logprobs": null,\
    "finish_reason": "stop"\
  }],
  "service_tier": "default",
  "usage": {
    "prompt_tokens": 9,
    "completion_tokens": 12,
    "total_tokens": 21,
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    }
  }
}
```

## The chat completion object

Represents a chat completion response returned by model, based on the provided input.

id

string

A unique identifier for the chat completion.

choices

array

A list of chat completion choices. Can be more than one if `n` is greater than 1.

Show properties

created

integer

The Unix timestamp (in seconds) of when the chat completion was created.

model

string

The model used for the chat completion.

service\_tier

string or null

The service tier used for processing the request.

system\_fingerprint

string

This fingerprint represents the backend configuration that the model runs with.

Can be used in conjunction with the `seed` request parameter to understand when backend changes have been made that might impact determinism.

object

string

The object type, which is always `chat.completion`.

usage

object

Usage statistics for the completion request.

Show properties

OBJECT The chat completion object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
{
  "id": "chatcmpl-123456",
  "object": "chat.completion",
  "created": 1728933352,
  "model": "gpt-4o-2024-08-06",
  "choices": [\
    {\
      "index": 0,\
      "message": {\
        "role": "assistant",\
        "content": "Hi there! How can I assist you today?",\
        "refusal": null\
      },\
      "logprobs": null,\
      "finish_reason": "stop"\
    }\
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 10,
    "total_tokens": 29,
    "prompt_tokens_details": {
      "cached_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    }
  },
  "system_fingerprint": "fp_6b68a8204b"
}
```

## The chat completion chunk object

Represents a streamed chunk of a chat completion response returned by model, based on the provided input.

id

string

A unique identifier for the chat completion. Each chunk has the same ID.

choices

array

A list of chat completion choices. Can contain more than one elements if `n` is greater than 1. Can also be empty for the
last chunk if you set `stream_options: {"include_usage": true}`.

Show properties

created

integer

The Unix timestamp (in seconds) of when the chat completion was created. Each chunk has the same timestamp.

model

string

The model to generate the completion.

service\_tier

string or null

The service tier used for processing the request.

system\_fingerprint

string

This fingerprint represents the backend configuration that the model runs with.
Can be used in conjunction with the `seed` request parameter to understand when backend changes have been made that might impact determinism.

object

string

The object type, which is always `chat.completion.chunk`.

usage

object or null

An optional field that will only be present when you set `stream_options: {"include_usage": true}` in your request.
When present, it contains a null value except for the last chunk which contains the token usage statistics for the entire request.

Show properties

OBJECT The chat completion chunk object

```JSON
1
2
3
4
5
6
7
{"id":"chatcmpl-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o-mini", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{"role":"assistant","content":""},"logprobs":null,"finish_reason":null}]}

{"id":"chatcmpl-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o-mini", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{"content":"Hello"},"logprobs":null,"finish_reason":null}]}

....

{"id":"chatcmpl-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o-mini", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{},"logprobs":null,"finish_reason":"stop"}]}
```

## Embeddings

Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.
Related guide: [Embeddings](https://platform.openai.com/docs/guides/embeddings)

## Create embeddings

posthttps://api.openai.com/v1/embeddings

Creates an embedding vector representing the input text.

### Request body

input

string or array

Required

Input text to embed, encoded as a string or array of tokens. To embed multiple inputs in a single request, pass an array of strings or array of token arrays. The input must not exceed the max input tokens for the model (8192 tokens for `text-embedding-ada-002`), cannot be an empty string, and any array must be 2048 dimensions or less. [Example Python code](https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken) for counting tokens. Some models may also impose a limit on total number of tokens summed across inputs.

Show possible types

model

string

Required

ID of the model to use. You can use the [List models](https://platform.openai.com/docs/api-reference/models/list) API to see all of your available models, or see our [Model overview](https://platform.openai.com/docs/models) for descriptions of them.

encoding\_format

string

Optional

Defaults to float

The format to return the embeddings in. Can be either `float` or [`base64`](https://pypi.org/project/pybase64/).

dimensions

integer

Optional

The number of dimensions the resulting output embeddings should have. Only supported in `text-embedding-3` and later models.

user

string

Optional

A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

### Returns

A list of [embedding](https://platform.openai.com/docs/api-reference/embeddings/object) objects.

Example request

curl

```bash
1
2
3
4
5
6
7
8
curl https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "The food was delicious and the waiter...",
    "model": "text-embedding-ada-002",
    "encoding_format": "float"
  }'
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

client.embeddings.create(
  model="text-embedding-ada-002",
  input="The food was delicious and the waiter...",
  encoding_format="float"
)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const embedding = await openai.embeddings.create({
    model: "text-embedding-ada-002",
    input: "The quick brown fox jumped over the lazy dog",
    encoding_format: "float",
  });

  console.log(embedding);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "object": "list",
  "data": [\
    {\
      "object": "embedding",\
      "embedding": [\
        0.0023064255,\
        -0.009327292,\
        .... (1536 floats total for ada-002)\
        -0.0028842222,\
      ],\
      "index": 0\
    }\
  ],
  "model": "text-embedding-ada-002",
  "usage": {
    "prompt_tokens": 8,
    "total_tokens": 8
  }
}
```

## The embedding object

Represents an embedding vector returned by embedding endpoint.

index

integer

The index of the embedding in the list of embeddings.

embedding

array

The embedding vector, which is a list of floats. The length of vector depends on the model as listed in the [embedding guide](https://platform.openai.com/docs/guides/embeddings).

object

string

The object type, which is always "embedding".

OBJECT The embedding object

```JSON
1
2
3
4
5
6
7
8
9
10
{
  "object": "embedding",
  "embedding": [\
    0.0023064255,\
    -0.009327292,\
    .... (1536 floats total for ada-002)\
    -0.0028842222,\
  ],
  "index": 0
}
```

## Fine-tuning

Manage fine-tuning jobs to tailor a model to your specific training data.
Related guide: [Fine-tune models](https://platform.openai.com/docs/guides/fine-tuning)

## Create fine-tuning job

posthttps://api.openai.com/v1/fine\_tuning/jobs

Creates a fine-tuning job which begins the process of creating a new model from a given dataset.

Response includes details of the enqueued job including job status and the name of the fine-tuned models once complete.

[Learn more about fine-tuning](https://platform.openai.com/docs/guides/fine-tuning)

### Request body

model

string

Required

The name of the model to fine-tune. You can select one of the
[supported models](https://platform.openai.com/docs/guides/fine-tuning#which-models-can-be-fine-tuned).

training\_file

string

Required

The ID of an uploaded file that contains training data.

See [upload file](https://platform.openai.com/docs/api-reference/files/create) for how to upload a file.

Your dataset must be formatted as a JSONL file. Additionally, you must upload your file with the purpose `fine-tune`.

The contents of the file should differ depending on if the model uses the [chat](https://platform.openai.com/docs/api-reference/fine-tuning/chat-input), [completions](https://platform.openai.com/docs/api-reference/fine-tuning/completions-input) format, or if the fine-tuning method uses the [preference](https://platform.openai.com/docs/api-reference/fine-tuning/preference-input) format.

See the [fine-tuning guide](https://platform.openai.com/docs/guides/fine-tuning) for more details.

hyperparameters

Deprecated

object

Optional

The hyperparameters used for the fine-tuning job.
This value is now deprecated in favor of `method`, and should be passed in under the `method` parameter.

Show properties

suffix

string or null

Optional

Defaults to null

A string of up to 64 characters that will be added to your fine-tuned model name.

For example, a `suffix` of "custom-model-name" would produce a model name like `ft:gpt-4o-mini:openai:custom-model-name:7p4lURel`.

validation\_file

string or null

Optional

The ID of an uploaded file that contains validation data.

If you provide this file, the data is used to generate validation
metrics periodically during fine-tuning. These metrics can be viewed in
the fine-tuning results file.
The same data should not be present in both train and validation files.

Your dataset must be formatted as a JSONL file. You must upload your file with the purpose `fine-tune`.

See the [fine-tuning guide](https://platform.openai.com/docs/guides/fine-tuning) for more details.

integrations

array or null

Optional

A list of integrations to enable for your fine-tuning job.

Show properties

seed

integer or null

Optional

The seed controls the reproducibility of the job. Passing in the same seed and job parameters should produce the same results, but may differ in rare cases.
If a seed is not specified, one will be generated for you.

method

object

Optional

The method used for fine-tuning.

Show properties

### Returns

A [fine-tuning.job](https://platform.openai.com/docs/api-reference/fine-tuning/object) object.

DefaultDefaultEpochsEpochsValidation fileValidation fileDPODPOW&B IntegrationW&B Integration

Example request

curl

```bash
1
2
3
4
5
6
7
curl https://api.openai.com/v1/fine_tuning/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "training_file": "file-BK7bzQj3FfZFXr7DbL6xJwfo",
    "model": "gpt-4o-mini"
  }'
```

```python
1
2
3
4
5
6
7
from openai import OpenAI
client = OpenAI()

client.fine_tuning.jobs.create(
  training_file="file-abc123",
  model="gpt-4o-mini"
)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const fineTune = await openai.fineTuning.jobs.create({
    training_file: "file-abc123"
  });

  console.log(fineTune);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
{
  "object": "fine_tuning.job",
  "id": "ftjob-abc123",
  "model": "gpt-4o-mini-2024-07-18",
  "created_at": 1721764800,
  "fine_tuned_model": null,
  "organization_id": "org-123",
  "result_files": [],
  "status": "queued",
  "validation_file": null,
  "training_file": "file-abc123",
  "method": {
    "type": "supervised",
    "supervised": {
      "hyperparameters": {
        "batch_size": "auto",
        "learning_rate_multiplier": "auto",
        "n_epochs": "auto",
      }
    }
  }
}
```

## List fine-tuning jobs

gethttps://api.openai.com/v1/fine\_tuning/jobs

List your organization's fine-tuning jobs

### Query parameters

after

string

Optional

Identifier for the last job from the previous pagination request.

limit

integer

Optional

Defaults to 20

Number of fine-tuning jobs to retrieve.

### Returns

A list of paginated [fine-tuning job](https://platform.openai.com/docs/api-reference/fine-tuning/object) objects.

Example request

curl

```bash
1
2
curl https://api.openai.com/v1/fine_tuning/jobs?limit=2 \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

client.fine_tuning.jobs.list()
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const list = await openai.fineTuning.jobs.list();

  for await (const fineTune of list) {
    console.log(fineTune);
  }
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
{
  "object": "list",
  "data": [\
    {\
      "object": "fine_tuning.job.event",\
      "id": "ft-event-TjX0lMfOniCZX64t9PUQT5hn",\
      "created_at": 1689813489,\
      "level": "warn",\
      "message": "Fine tuning process stopping due to job cancellation",\
      "data": null,\
      "type": "message"\
    },\
    { ... },\
    { ... }\
  ], "has_more": true
}
```

## List fine-tuning events

gethttps://api.openai.com/v1/fine\_tuning/jobs/{fine\_tuning\_job\_id}/events

Get status updates for a fine-tuning job.

### Path parameters

fine\_tuning\_job\_id

string

Required

The ID of the fine-tuning job to get events for.

### Query parameters

after

string

Optional

Identifier for the last event from the previous pagination request.

limit

integer

Optional

Defaults to 20

Number of events to retrieve.

### Returns

A list of fine-tuning event objects.

Example request

curl

```bash
1
2
curl https://api.openai.com/v1/fine_tuning/jobs/ftjob-abc123/events \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

```python
1
2
3
4
5
6
7
from openai import OpenAI
client = OpenAI()

client.fine_tuning.jobs.list_events(
  fine_tuning_job_id="ftjob-abc123",
  limit=2
)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const list = await openai.fineTuning.list_events(id="ftjob-abc123", limit=2);

  for await (const fineTune of list) {
    console.log(fineTune);
  }
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
{
  "object": "list",
  "data": [\
    {\
      "object": "fine_tuning.job.event",\
      "id": "ft-event-ddTJfwuMVpfLXseO0Am0Gqjm",\
      "created_at": 1721764800,\
      "level": "info",\
      "message": "Fine tuning job successfully completed",\
      "data": null,\
      "type": "message"\
    },\
    {\
      "object": "fine_tuning.job.event",\
      "id": "ft-event-tyiGuB72evQncpH87xe505Sv",\
      "created_at": 1721764800,\
      "level": "info",\
      "message": "New fine-tuned model created: ft:gpt-4o-mini:openai::7p4lURel",\
      "data": null,\
      "type": "message"\
    }\
  ],
  "has_more": true
}
```

## List fine-tuning checkpoints

gethttps://api.openai.com/v1/fine\_tuning/jobs/{fine\_tuning\_job\_id}/checkpoints

List checkpoints for a fine-tuning job.

### Path parameters

fine\_tuning\_job\_id

string

Required

The ID of the fine-tuning job to get checkpoints for.

### Query parameters

after

string

Optional

Identifier for the last checkpoint ID from the previous pagination request.

limit

integer

Optional

Defaults to 10

Number of checkpoints to retrieve.

### Returns

A list of fine-tuning [checkpoint objects](https://platform.openai.com/docs/api-reference/fine-tuning/checkpoint-object) for a fine-tuning job.

Example request

curl

```bash
1
2
curl https://api.openai.com/v1/fine_tuning/jobs/ftjob-abc123/checkpoints \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
{
  "object": "list"
  "data": [\
    {\
      "object": "fine_tuning.job.checkpoint",\
      "id": "ftckpt_zc4Q7MP6XxulcVzj4MZdwsAB",\
      "created_at": 1721764867,\
      "fine_tuned_model_checkpoint": "ft:gpt-4o-mini-2024-07-18:my-org:custom-suffix:96olL566:ckpt-step-2000",\
      "metrics": {\
        "full_valid_loss": 0.134,\
        "full_valid_mean_token_accuracy": 0.874\
      },\
      "fine_tuning_job_id": "ftjob-abc123",\
      "step_number": 2000,\
    },\
    {\
      "object": "fine_tuning.job.checkpoint",\
      "id": "ftckpt_enQCFmOTGj3syEpYVhBRLTSy",\
      "created_at": 1721764800,\
      "fine_tuned_model_checkpoint": "ft:gpt-4o-mini-2024-07-18:my-org:custom-suffix:7q8mpxmy:ckpt-step-1000",\
      "metrics": {\
        "full_valid_loss": 0.167,\
        "full_valid_mean_token_accuracy": 0.781\
      },\
      "fine_tuning_job_id": "ftjob-abc123",\
      "step_number": 1000,\
    },\
  ],
  "first_id": "ftckpt_zc4Q7MP6XxulcVzj4MZdwsAB",
  "last_id": "ftckpt_enQCFmOTGj3syEpYVhBRLTSy",
  "has_more": true
}
```

## Retrieve fine-tuning job

gethttps://api.openai.com/v1/fine\_tuning/jobs/{fine\_tuning\_job\_id}

Get info about a fine-tuning job.

[Learn more about fine-tuning](https://platform.openai.com/docs/guides/fine-tuning)

### Path parameters

fine\_tuning\_job\_id

string

Required

The ID of the fine-tuning job.

### Returns

The [fine-tuning](https://platform.openai.com/docs/api-reference/fine-tuning/object) object with the given ID.

Example request

curl

```bash
1
2
curl https://api.openai.com/v1/fine_tuning/jobs/ft-AF1WoRqd3aJAHsqc9NY7iL8F \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

client.fine_tuning.jobs.retrieve("ftjob-abc123")
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const fineTune = await openai.fineTuning.jobs.retrieve("ftjob-abc123");

  console.log(fineTune);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
{
  "object": "fine_tuning.job",
  "id": "ftjob-abc123",
  "model": "davinci-002",
  "created_at": 1692661014,
  "finished_at": 1692661190,
  "fine_tuned_model": "ft:davinci-002:my-org:custom_suffix:7q8mpxmy",
  "organization_id": "org-123",
  "result_files": [\
      "file-abc123"\
  ],
  "status": "succeeded",
  "validation_file": null,
  "training_file": "file-abc123",
  "hyperparameters": {
      "n_epochs": 4,
      "batch_size": 1,
      "learning_rate_multiplier": 1.0
  },
  "trained_tokens": 5768,
  "integrations": [],
  "seed": 0,
  "estimated_finish": 0,
  "method": {
    "type": "supervised",
    "supervised": {
      "hyperparameters": {
        "n_epochs": 4,
        "batch_size": 1,
        "learning_rate_multiplier": 1.0
      }
    }
  }
}
```

## Cancel fine-tuning

posthttps://api.openai.com/v1/fine\_tuning/jobs/{fine\_tuning\_job\_id}/cancel

Immediately cancel a fine-tune job.

### Path parameters

fine\_tuning\_job\_id

string

Required

The ID of the fine-tuning job to cancel.

### Returns

The cancelled [fine-tuning](https://platform.openai.com/docs/api-reference/fine-tuning/object) object.

Example request

curl

```bash
1
2
curl -X POST https://api.openai.com/v1/fine_tuning/jobs/ftjob-abc123/cancel \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

client.fine_tuning.jobs.cancel("ftjob-abc123")
```

```javascript
1
2
3
4
5
6
7
8
9
10
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const fineTune = await openai.fineTuning.jobs.cancel("ftjob-abc123");

  console.log(fineTune);
}
main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
{
  "object": "fine_tuning.job",
  "id": "ftjob-abc123",
  "model": "gpt-4o-mini-2024-07-18",
  "created_at": 1721764800,
  "fine_tuned_model": null,
  "organization_id": "org-123",
  "result_files": [],
  "status": "cancelled",
  "validation_file": "file-abc123",
  "training_file": "file-abc123"
}
```

## Training format for chat models using the supervised method

The per-line training example of a fine-tuning input file for chat models using the supervised method.

messages

array

Show possible types

tools

array

A list of tools the model may generate JSON inputs for.

Show properties

parallel\_tool\_calls

boolean

Whether to enable [parallel function calling](https://platform.openai.com/docs/guides/function-calling#configuring-parallel-function-calling) during tool use.

functions

Deprecated

array

A list of functions the model may generate JSON inputs for.

Show properties

OBJECT Training format for chat models using the supervised method

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
{
  "messages": [\
    { "role": "user", "content": "What is the weather in San Francisco?" },\
    {\
      "role": "assistant",\
      "tool_calls": [\
        {\
          "id": "call_id",\
          "type": "function",\
          "function": {\
            "name": "get_current_weather",\
            "arguments": "{\"location\": \"San Francisco, USA\", \"format\": \"celsius\"}"\
          }\
        }\
      ]\
    }\
  ],
  "parallel_tool_calls": false,
  "tools": [\
    {\
      "type": "function",\
      "function": {\
        "name": "get_current_weather",\
        "description": "Get the current weather",\
        "parameters": {\
          "type": "object",\
          "properties": {\
            "location": {\
                "type": "string",\
                "description": "The city and country, eg. San Francisco, USA"\
            },\
            "format": { "type": "string", "enum": ["celsius", "fahrenheit"] }\
          },\
          "required": ["location", "format"]\
        }\
      }\
    }\
  ]
}
```

## Training format for chat models using the preference method

The per-line training example of a fine-tuning input file for chat models using the dpo method.

input

object

Show properties

preferred\_completion

array

The preferred completion message for the output.

Show possible types

non\_preferred\_completion

array

The non-preferred completion message for the output.

Show possible types

OBJECT Training format for chat models using the preference method

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
{
  "input": {
    "messages": [\
      { "role": "user", "content": "What is the weather in San Francisco?" }\
    ]
  },
  "preferred_completion": [\
    {\
      "role": "assistant",\
      "content": "The weather in San Francisco is 70 degrees Fahrenheit."\
    }\
  ],
  "non_preferred_completion": [\
    {\
      "role": "assistant",\
      "content": "The weather in San Francisco is 21 degrees Celsius."\
    }\
  ]
}
```

## Training format for completions models

The per-line training example of a fine-tuning input file for completions models

prompt

string

The input prompt for this training example.

completion

string

The desired completion for this training example.

OBJECT Training format for completions models

```JSON
1
2
3
4
{
  "prompt": "What is the answer to 2+2",
  "completion": "4"
}
```

## The fine-tuning job object

The `fine_tuning.job` object represents a fine-tuning job that has been created through the API.

id

string

The object identifier, which can be referenced in the API endpoints.

created\_at

integer

The Unix timestamp (in seconds) for when the fine-tuning job was created.

error

object or null

For fine-tuning jobs that have `failed`, this will contain more information on the cause of the failure.

Show properties

fine\_tuned\_model

string or null

The name of the fine-tuned model that is being created. The value will be null if the fine-tuning job is still running.

finished\_at

integer or null

The Unix timestamp (in seconds) for when the fine-tuning job was finished. The value will be null if the fine-tuning job is still running.

hyperparameters

object

The hyperparameters used for the fine-tuning job. This value will only be returned when running `supervised` jobs.

Show properties

model

string

The base model that is being fine-tuned.

object

string

The object type, which is always "fine\_tuning.job".

organization\_id

string

The organization that owns the fine-tuning job.

result\_files

array

The compiled results file ID(s) for the fine-tuning job. You can retrieve the results with the [Files API](https://platform.openai.com/docs/api-reference/files/retrieve-contents).

status

string

The current status of the fine-tuning job, which can be either `validating_files`, `queued`, `running`, `succeeded`, `failed`, or `cancelled`.

trained\_tokens

integer or null

The total number of billable tokens processed by this fine-tuning job. The value will be null if the fine-tuning job is still running.

training\_file

string

The file ID used for training. You can retrieve the training data with the [Files API](https://platform.openai.com/docs/api-reference/files/retrieve-contents).

validation\_file

string or null

The file ID used for validation. You can retrieve the validation results with the [Files API](https://platform.openai.com/docs/api-reference/files/retrieve-contents).

integrations

array or null

A list of integrations to enable for this fine-tuning job.

Show possible types

seed

integer

The seed used for the fine-tuning job.

estimated\_finish

integer or null

The Unix timestamp (in seconds) for when the fine-tuning job is estimated to finish. The value will be null if the fine-tuning job is not running.

method

object

The method used for fine-tuning.

Show properties

OBJECT The fine-tuning job object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
{
  "object": "fine_tuning.job",
  "id": "ftjob-abc123",
  "model": "davinci-002",
  "created_at": 1692661014,
  "finished_at": 1692661190,
  "fine_tuned_model": "ft:davinci-002:my-org:custom_suffix:7q8mpxmy",
  "organization_id": "org-123",
  "result_files": [\
      "file-abc123"\
  ],
  "status": "succeeded",
  "validation_file": null,
  "training_file": "file-abc123",
  "hyperparameters": {
      "n_epochs": 4,
      "batch_size": 1,
      "learning_rate_multiplier": 1.0
  },
  "trained_tokens": 5768,
  "integrations": [],
  "seed": 0,
  "estimated_finish": 0,
  "method": {
    "type": "supervised",
    "supervised": {
      "hyperparameters": {
        "n_epochs": 4,
        "batch_size": 1,
        "learning_rate_multiplier": 1.0
      }
    }
  }
}
```

## The fine-tuning job event object

Fine-tuning job event object

object

string

The object type, which is always "fine\_tuning.job.event".

id

string

The object identifier.

created\_at

integer

The Unix timestamp (in seconds) for when the fine-tuning job was created.

level

string

The log level of the event.

message

string

The message of the event.

type

string

The type of event.

data

object

The data associated with the event.

OBJECT The fine-tuning job event object

```JSON
1
2
3
4
5
6
7
8
9
{
  "object": "fine_tuning.job.event",
  "id": "ftevent-abc123"
  "created_at": 1677610602,
  "level": "info",
  "message": "Created fine-tuning job",
  "data": {},
  "type": "message"
}
```

## The fine-tuning job checkpoint object

The `fine_tuning.job.checkpoint` object represents a model checkpoint for a fine-tuning job that is ready to use.

id

string

The checkpoint identifier, which can be referenced in the API endpoints.

created\_at

integer

The Unix timestamp (in seconds) for when the checkpoint was created.

fine\_tuned\_model\_checkpoint

string

The name of the fine-tuned checkpoint model that is created.

step\_number

integer

The step number that the checkpoint was created at.

metrics

object

Metrics at the step number during the fine-tuning job.

Show properties

fine\_tuning\_job\_id

string

The name of the fine-tuning job that this checkpoint was created from.

object

string

The object type, which is always "fine\_tuning.job.checkpoint".

OBJECT The fine-tuning job checkpoint object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
{
  "object": "fine_tuning.job.checkpoint",
  "id": "ftckpt_qtZ5Gyk4BLq1SfLFWp3RtO3P",
  "created_at": 1712211699,
  "fine_tuned_model_checkpoint": "ft:gpt-4o-mini-2024-07-18:my-org:custom_suffix:9ABel2dg:ckpt-step-88",
  "fine_tuning_job_id": "ftjob-fpbNQ3H1GrMehXRf8cO97xTN",
  "metrics": {
    "step": 88,
    "train_loss": 0.478,
    "train_mean_token_accuracy": 0.924,
    "valid_loss": 10.112,
    "valid_mean_token_accuracy": 0.145,
    "full_valid_loss": 0.567,
    "full_valid_mean_token_accuracy": 0.944
  },
  "step_number": 88
}
```

## Batch

Create large batches of API requests for asynchronous processing. The Batch API returns completions within 24 hours for a 50% discount.
Related guide: [Batch](https://platform.openai.com/docs/guides/batch)

## Create batch

posthttps://api.openai.com/v1/batches

Creates and executes a batch from an uploaded file of requests

### Request body

input\_file\_id

string

Required

The ID of an uploaded file that contains requests for the new batch.

See [upload file](https://platform.openai.com/docs/api-reference/files/create) for how to upload a file.

Your input file must be formatted as a [JSONL file](https://platform.openai.com/docs/api-reference/batch/request-input), and must be uploaded with the purpose `batch`. The file can contain up to 50,000 requests, and can be up to 200 MB in size.

endpoint

string

Required

The endpoint to be used for all requests in the batch. Currently `/v1/chat/completions`, `/v1/embeddings`, and `/v1/completions` are supported. Note that `/v1/embeddings` batches are also restricted to a maximum of 50,000 embedding inputs across all requests in the batch.

completion\_window

string

Required

The time frame within which the batch should be processed. Currently only `24h` is supported.

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

### Returns

The created [Batch](https://platform.openai.com/docs/api-reference/batch/object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
8
curl https://api.openai.com/v1/batches \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input_file_id": "file-abc123",
    "endpoint": "/v1/chat/completions",
    "completion_window": "24h"
  }'
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

client.batches.create(
  input_file_id="file-abc123",
  endpoint="/v1/chat/completions",
  completion_window="24h"
)
```

```node
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const batch = await openai.batches.create({
    input_file_id: "file-abc123",
    endpoint: "/v1/chat/completions",
    completion_window: "24h"
  });

  console.log(batch);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
{
  "id": "batch_abc123",
  "object": "batch",
  "endpoint": "/v1/chat/completions",
  "errors": null,
  "input_file_id": "file-abc123",
  "completion_window": "24h",
  "status": "validating",
  "output_file_id": null,
  "error_file_id": null,
  "created_at": 1711471533,
  "in_progress_at": null,
  "expires_at": null,
  "finalizing_at": null,
  "completed_at": null,
  "failed_at": null,
  "expired_at": null,
  "cancelling_at": null,
  "cancelled_at": null,
  "request_counts": {
    "total": 0,
    "completed": 0,
    "failed": 0
  },
  "metadata": {
    "customer_id": "user_123456789",
    "batch_description": "Nightly eval job",
  }
}
```

## Retrieve batch

gethttps://api.openai.com/v1/batches/{batch\_id}

Retrieves a batch.

### Path parameters

batch\_id

string

Required

The ID of the batch to retrieve.

### Returns

The [Batch](https://platform.openai.com/docs/api-reference/batch/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/batches/batch_abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

client.batches.retrieve("batch_abc123")
```

```node
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const batch = await openai.batches.retrieve("batch_abc123");

  console.log(batch);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
{
  "id": "batch_abc123",
  "object": "batch",
  "endpoint": "/v1/completions",
  "errors": null,
  "input_file_id": "file-abc123",
  "completion_window": "24h",
  "status": "completed",
  "output_file_id": "file-cvaTdG",
  "error_file_id": "file-HOWS94",
  "created_at": 1711471533,
  "in_progress_at": 1711471538,
  "expires_at": 1711557933,
  "finalizing_at": 1711493133,
  "completed_at": 1711493163,
  "failed_at": null,
  "expired_at": null,
  "cancelling_at": null,
  "cancelled_at": null,
  "request_counts": {
    "total": 100,
    "completed": 95,
    "failed": 5
  },
  "metadata": {
    "customer_id": "user_123456789",
    "batch_description": "Nightly eval job",
  }
}
```

## Cancel batch

posthttps://api.openai.com/v1/batches/{batch\_id}/cancel

Cancels an in-progress batch. The batch will be in status `cancelling` for up to 10 minutes, before changing to `cancelled`, where it will have partial results (if any) available in the output file.

### Path parameters

batch\_id

string

Required

The ID of the batch to cancel.

### Returns

The [Batch](https://platform.openai.com/docs/api-reference/batch/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/batches/batch_abc123/cancel \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

client.batches.cancel("batch_abc123")
```

```node
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const batch = await openai.batches.cancel("batch_abc123");

  console.log(batch);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
{
  "id": "batch_abc123",
  "object": "batch",
  "endpoint": "/v1/chat/completions",
  "errors": null,
  "input_file_id": "file-abc123",
  "completion_window": "24h",
  "status": "cancelling",
  "output_file_id": null,
  "error_file_id": null,
  "created_at": 1711471533,
  "in_progress_at": 1711471538,
  "expires_at": 1711557933,
  "finalizing_at": null,
  "completed_at": null,
  "failed_at": null,
  "expired_at": null,
  "cancelling_at": 1711475133,
  "cancelled_at": null,
  "request_counts": {
    "total": 100,
    "completed": 23,
    "failed": 1
  },
  "metadata": {
    "customer_id": "user_123456789",
    "batch_description": "Nightly eval job",
  }
}
```

## List batch

gethttps://api.openai.com/v1/batches

List your organization's batches.

### Query parameters

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

### Returns

A list of paginated [Batch](https://platform.openai.com/docs/api-reference/batch/object) objects.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/batches?limit=2 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json"
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

client.batches.list()
```

```node
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const list = await openai.batches.list();

  for await (const batch of list) {
    console.log(batch);
  }
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
{
  "object": "list",
  "data": [\
    {\
      "id": "batch_abc123",\
      "object": "batch",\
      "endpoint": "/v1/chat/completions",\
      "errors": null,\
      "input_file_id": "file-abc123",\
      "completion_window": "24h",\
      "status": "completed",\
      "output_file_id": "file-cvaTdG",\
      "error_file_id": "file-HOWS94",\
      "created_at": 1711471533,\
      "in_progress_at": 1711471538,\
      "expires_at": 1711557933,\
      "finalizing_at": 1711493133,\
      "completed_at": 1711493163,\
      "failed_at": null,\
      "expired_at": null,\
      "cancelling_at": null,\
      "cancelled_at": null,\
      "request_counts": {\
        "total": 100,\
        "completed": 95,\
        "failed": 5\
      },\
      "metadata": {\
        "customer_id": "user_123456789",\
        "batch_description": "Nightly job",\
      }\
    },\
    { ... },\
  ],
  "first_id": "batch_abc123",
  "last_id": "batch_abc456",
  "has_more": true
}
```

## The batch object

id

string

object

string

The object type, which is always `batch`.

endpoint

string

The OpenAI API endpoint used by the batch.

errors

object

Show properties

input\_file\_id

string

The ID of the input file for the batch.

completion\_window

string

The time frame within which the batch should be processed.

status

string

The current status of the batch.

output\_file\_id

string

The ID of the file containing the outputs of successfully executed requests.

error\_file\_id

string

The ID of the file containing the outputs of requests with errors.

created\_at

integer

The Unix timestamp (in seconds) for when the batch was created.

in\_progress\_at

integer

The Unix timestamp (in seconds) for when the batch started processing.

expires\_at

integer

The Unix timestamp (in seconds) for when the batch will expire.

finalizing\_at

integer

The Unix timestamp (in seconds) for when the batch started finalizing.

completed\_at

integer

The Unix timestamp (in seconds) for when the batch was completed.

failed\_at

integer

The Unix timestamp (in seconds) for when the batch failed.

expired\_at

integer

The Unix timestamp (in seconds) for when the batch expired.

cancelling\_at

integer

The Unix timestamp (in seconds) for when the batch started cancelling.

cancelled\_at

integer

The Unix timestamp (in seconds) for when the batch was cancelled.

request\_counts

object

The request counts for different statuses within the batch.

Show properties

metadata

map

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

OBJECT The batch object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
{
  "id": "batch_abc123",
  "object": "batch",
  "endpoint": "/v1/completions",
  "errors": null,
  "input_file_id": "file-abc123",
  "completion_window": "24h",
  "status": "completed",
  "output_file_id": "file-cvaTdG",
  "error_file_id": "file-HOWS94",
  "created_at": 1711471533,
  "in_progress_at": 1711471538,
  "expires_at": 1711557933,
  "finalizing_at": 1711493133,
  "completed_at": 1711493163,
  "failed_at": null,
  "expired_at": null,
  "cancelling_at": null,
  "cancelled_at": null,
  "request_counts": {
    "total": 100,
    "completed": 95,
    "failed": 5
  },
  "metadata": {
    "customer_id": "user_123456789",
    "batch_description": "Nightly eval job",
  }
}
```

## The request input object

The per-line object of the batch input file

custom\_id

string

A developer-provided per-request id that will be used to match outputs to inputs. Must be unique for each request in a batch.

method

string

The HTTP method to be used for the request. Currently only `POST` is supported.

url

string

The OpenAI API relative URL to be used for the request. Currently `/v1/chat/completions`, `/v1/embeddings`, and `/v1/completions` are supported.

OBJECT The request input object

```JSON
{"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is 2+2?"}]}}
```

## The request output object

The per-line object of the batch output and error files

id

string

custom\_id

string

A developer-provided per-request id that will be used to match outputs to inputs.

response

object or null

Show properties

error

object or null

For requests that failed with a non-HTTP error, this will contain more information on the cause of the failure.

Show properties

OBJECT The request output object

```JSON
{"id": "batch_req_wnaDys", "custom_id": "request-2", "response": {"status_code": 200, "request_id": "req_c187b3", "body": {"id": "chatcmpl-9758Iw", "object": "chat.completion", "created": 1711475054, "model": "gpt-4o-mini", "choices": [{"index": 0, "message": {"role": "assistant", "content": "2 + 2 equals 4."}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 24, "completion_tokens": 15, "total_tokens": 39}, "system_fingerprint": null}}, "error": null}
```

## Files

Files are used to upload documents that can be used with features like [Assistants](https://platform.openai.com/docs/api-reference/assistants), [Fine-tuning](https://platform.openai.com/docs/api-reference/fine-tuning), and [Batch API](https://platform.openai.com/docs/guides/batch).

## Upload file

posthttps://api.openai.com/v1/files

Upload a file that can be used across various endpoints. Individual files can be up to 512 MB, and the size of all files uploaded by one organization can be up to 100 GB.

The Assistants API supports files up to 2 million tokens and of specific file types. See the [Assistants Tools guide](https://platform.openai.com/docs/assistants/tools) for details.

The Fine-tuning API only supports `.jsonl` files. The input also has certain required formats for fine-tuning [chat](https://platform.openai.com/docs/api-reference/fine-tuning/chat-input) or [completions](https://platform.openai.com/docs/api-reference/fine-tuning/completions-input) models.

The Batch API only supports `.jsonl` files up to 200 MB in size. The input also has a specific required [format](https://platform.openai.com/docs/api-reference/batch/request-input).

Please [contact us](https://help.openai.com/) if you need to increase these storage limits.

### Request body

file

file

Required

The File object (not file name) to be uploaded.

purpose

string

Required

The intended purpose of the uploaded file.

Use "assistants" for [Assistants](https://platform.openai.com/docs/api-reference/assistants) and [Message](https://platform.openai.com/docs/api-reference/messages) files, "vision" for Assistants image file inputs, "batch" for [Batch API](https://platform.openai.com/docs/guides/batch), and "fine-tune" for [Fine-tuning](https://platform.openai.com/docs/api-reference/fine-tuning).

### Returns

The uploaded [File](https://platform.openai.com/docs/api-reference/files/object) object.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F purpose="fine-tune" \
  -F file="@mydata.jsonl"
```

```python
1
2
3
4
5
6
7
from openai import OpenAI
client = OpenAI()

client.files.create(
  file=open("mydata.jsonl", "rb"),
  purpose="fine-tune"
)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
import fs from "fs";
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const file = await openai.files.create({
    file: fs.createReadStream("mydata.jsonl"),
    purpose: "fine-tune",
  });

  console.log(file);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
{
  "id": "file-abc123",
  "object": "file",
  "bytes": 120000,
  "created_at": 1677610602,
  "filename": "mydata.jsonl",
  "purpose": "fine-tune",
}
```

## List files

gethttps://api.openai.com/v1/files

Returns a list of files.

### Query parameters

purpose

string

Optional

Only return files with the given purpose.

limit

integer

Optional

Defaults to 10000

A limit on the number of objects to be returned. Limit can range between 1 and 10,000, and the default is 10,000.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

### Returns

A list of [File](https://platform.openai.com/docs/api-reference/files/object) objects.

Example request

curl

```bash
1
2
curl https://api.openai.com/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

client.files.list()
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const list = await openai.files.list();

  for await (const file of list) {
    console.log(file);
  }
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
{
  "data": [\
    {\
      "id": "file-abc123",\
      "object": "file",\
      "bytes": 175,\
      "created_at": 1613677385,\
      "filename": "salesOverview.pdf",\
      "purpose": "assistants",\
    },\
    {\
      "id": "file-abc123",\
      "object": "file",\
      "bytes": 140,\
      "created_at": 1613779121,\
      "filename": "puppy.jsonl",\
      "purpose": "fine-tune",\
    }\
  ],
  "object": "list"
}
```

## Retrieve file

gethttps://api.openai.com/v1/files/{file\_id}

Returns information about a specific file.

### Path parameters

file\_id

string

Required

The ID of the file to use for this request.

### Returns

The [File](https://platform.openai.com/docs/api-reference/files/object) object matching the specified ID.

Example request

curl

```bash
1
2
curl https://api.openai.com/v1/files/file-abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

client.files.retrieve("file-abc123")
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const file = await openai.files.retrieve("file-abc123");

  console.log(file);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
{
  "id": "file-abc123",
  "object": "file",
  "bytes": 120000,
  "created_at": 1677610602,
  "filename": "mydata.jsonl",
  "purpose": "fine-tune",
}
```

## Delete file

deletehttps://api.openai.com/v1/files/{file\_id}

Delete a file.

### Path parameters

file\_id

string

Required

The ID of the file to use for this request.

### Returns

Deletion status.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/files/file-abc123 \
  -X DELETE \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

client.files.delete("file-abc123")
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const file = await openai.files.del("file-abc123");

  console.log(file);
}

main();
```

Response

```json
1
2
3
4
5
{
  "id": "file-abc123",
  "object": "file",
  "deleted": true
}
```

## Retrieve file content

gethttps://api.openai.com/v1/files/{file\_id}/content

Returns the contents of the specified file.

### Path parameters

file\_id

string

Required

The ID of the file to use for this request.

### Returns

The file content.

Example request

curl

```bash
1
2
curl https://api.openai.com/v1/files/file-abc123/content \
  -H "Authorization: Bearer $OPENAI_API_KEY" > file.jsonl
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

content = client.files.content("file-abc123")
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const file = await openai.files.content("file-abc123");

  console.log(file);
}

main();
```

## The file object

The `File` object represents a document that has been uploaded to OpenAI.

id

string

The file identifier, which can be referenced in the API endpoints.

bytes

integer

The size of the file, in bytes.

created\_at

integer

The Unix timestamp (in seconds) for when the file was created.

filename

string

The name of the file.

object

string

The object type, which is always `file`.

purpose

string

The intended purpose of the file. Supported values are `assistants`, `assistants_output`, `batch`, `batch_output`, `fine-tune`, `fine-tune-results` and `vision`.

status

Deprecated

string

Deprecated. The current status of the file, which can be either `uploaded`, `processed`, or `error`.

status\_details

Deprecated

string

Deprecated. For details on why a fine-tuning training file failed validation, see the `error` field on `fine_tuning.job`.

OBJECT The file object

```JSON
1
2
3
4
5
6
7
8
{
  "id": "file-abc123",
  "object": "file",
  "bytes": 120000,
  "created_at": 1677610602,
  "filename": "salesOverview.pdf",
  "purpose": "assistants",
}
```

## Uploads

Allows you to upload large files in multiple parts.

## Create upload

posthttps://api.openai.com/v1/uploads

Creates an intermediate [Upload](https://platform.openai.com/docs/api-reference/uploads/object) object that you can add [Parts](https://platform.openai.com/docs/api-reference/uploads/part-object) to. Currently, an Upload can accept at most 8 GB in total and expires after an hour after you create it.

Once you complete the Upload, we will create a [File](https://platform.openai.com/docs/api-reference/files/object) object that contains all the parts you uploaded. This File is usable in the rest of our platform as a regular File object.

For certain `purpose` s, the correct `mime_type` must be specified. Please refer to documentation for the supported MIME types for your use case:

- [Assistants](https://platform.openai.com/docs/assistants/tools/file-search#supported-files)

For guidance on the proper filename extensions for each purpose, please follow the documentation on [creating a File](https://platform.openai.com/docs/api-reference/files/create).

### Request body

filename

string

Required

The name of the file to upload.

purpose

string

Required

The intended purpose of the uploaded file.

See the [documentation on File purposes](https://platform.openai.com/docs/api-reference/files/create#files-create-purpose).

bytes

integer

Required

The number of bytes in the file you are uploading.

mime\_type

string

Required

The MIME type of the file.

This must fall within the supported MIME types for your file purpose. See the supported MIME types for assistants and vision.

### Returns

The [Upload](https://platform.openai.com/docs/api-reference/uploads/object) object with status `pending`.

Example request

curl

```bash
1
2
3
4
5
6
7
8
curl https://api.openai.com/v1/uploads \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "purpose": "fine-tune",
    "filename": "training_examples.jsonl",
    "bytes": 2147483648,
    "mime_type": "text/jsonl"
  }'
```

Response

```json
1
2
3
4
5
6
7
8
9
10
{
  "id": "upload_abc123",
  "object": "upload",
  "bytes": 2147483648,
  "created_at": 1719184911,
  "filename": "training_examples.jsonl",
  "purpose": "fine-tune",
  "status": "pending",
  "expires_at": 1719127296
}
```

## Add upload part

posthttps://api.openai.com/v1/uploads/{upload\_id}/parts

Adds a [Part](https://platform.openai.com/docs/api-reference/uploads/part-object) to an [Upload](https://platform.openai.com/docs/api-reference/uploads/object) object. A Part represents a chunk of bytes from the file you are trying to upload.

Each Part can be at most 64 MB, and you can add Parts until you hit the Upload maximum of 8 GB.

It is possible to add multiple Parts in parallel. You can decide the intended order of the Parts when you [complete the Upload](https://platform.openai.com/docs/api-reference/uploads/complete).

### Path parameters

upload\_id

string

Required

The ID of the Upload.

### Request body

data

file

Required

The chunk of bytes for this Part.

### Returns

The upload [Part](https://platform.openai.com/docs/api-reference/uploads/part-object) object.

Example request

curl

```bash
1
2
curl https://api.openai.com/v1/uploads/upload_abc123/parts
  -F data="aHR0cHM6Ly9hcGkub3BlbmFpLmNvbS92MS91cGxvYWRz..."
```

Response

```json
1
2
3
4
5
6
{
  "id": "part_def456",
  "object": "upload.part",
  "created_at": 1719185911,
  "upload_id": "upload_abc123"
}
```

## Complete upload

posthttps://api.openai.com/v1/uploads/{upload\_id}/complete

Completes the [Upload](https://platform.openai.com/docs/api-reference/uploads/object).

Within the returned Upload object, there is a nested [File](https://platform.openai.com/docs/api-reference/files/object) object that is ready to use in the rest of the platform.

You can specify the order of the Parts by passing in an ordered list of the Part IDs.

The number of bytes uploaded upon completion must match the number of bytes initially specified when creating the Upload object. No Parts may be added after an Upload is completed.

### Path parameters

upload\_id

string

Required

The ID of the Upload.

### Request body

part\_ids

array

Required

The ordered list of Part IDs.

md5

string

Optional

The optional md5 checksum for the file contents to verify if the bytes uploaded matches what you expect.

### Returns

The [Upload](https://platform.openai.com/docs/api-reference/uploads/object) object with status `completed` with an additional `file` property containing the created usable File object.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/uploads/upload_abc123/complete
  -d '{
    "part_ids": ["part_def456", "part_ghi789"]
  }'
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
{
  "id": "upload_abc123",
  "object": "upload",
  "bytes": 2147483648,
  "created_at": 1719184911,
  "filename": "training_examples.jsonl",
  "purpose": "fine-tune",
  "status": "completed",
  "expires_at": 1719127296,
  "file": {
    "id": "file-xyz321",
    "object": "file",
    "bytes": 2147483648,
    "created_at": 1719186911,
    "filename": "training_examples.jsonl",
    "purpose": "fine-tune",
  }
}
```

## Cancel upload

posthttps://api.openai.com/v1/uploads/{upload\_id}/cancel

Cancels the Upload. No Parts may be added after an Upload is cancelled.

### Path parameters

upload\_id

string

Required

The ID of the Upload.

### Returns

The [Upload](https://platform.openai.com/docs/api-reference/uploads/object) object with status `cancelled`.

Example request

curl

```bash
curl https://api.openai.com/v1/uploads/upload_abc123/cancel
```

Response

```json
1
2
3
4
5
6
7
8
9
10
{
  "id": "upload_abc123",
  "object": "upload",
  "bytes": 2147483648,
  "created_at": 1719184911,
  "filename": "training_examples.jsonl",
  "purpose": "fine-tune",
  "status": "cancelled",
  "expires_at": 1719127296
}
```

## The upload object

The Upload object can accept byte chunks in the form of Parts.

id

string

The Upload unique identifier, which can be referenced in API endpoints.

created\_at

integer

The Unix timestamp (in seconds) for when the Upload was created.

filename

string

The name of the file to be uploaded.

bytes

integer

The intended number of bytes to be uploaded.

purpose

string

The intended purpose of the file. [Please refer here](https://platform.openai.com/docs/api-reference/files/object#files/object-purpose) for acceptable values.

status

string

The status of the Upload.

expires\_at

integer

The Unix timestamp (in seconds) for when the Upload was created.

object

string

The object type, which is always "upload".

file

The `File` object represents a document that has been uploaded to OpenAI.

OBJECT The upload object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
{
  "id": "upload_abc123",
  "object": "upload",
  "bytes": 2147483648,
  "created_at": 1719184911,
  "filename": "training_examples.jsonl",
  "purpose": "fine-tune",
  "status": "completed",
  "expires_at": 1719127296,
  "file": {
    "id": "file-xyz321",
    "object": "file",
    "bytes": 2147483648,
    "created_at": 1719186911,
    "filename": "training_examples.jsonl",
    "purpose": "fine-tune",
  }
}
```

## The upload part object

The upload Part represents a chunk of bytes we can add to an Upload object.

id

string

The upload Part unique identifier, which can be referenced in API endpoints.

created\_at

integer

The Unix timestamp (in seconds) for when the Part was created.

upload\_id

string

The ID of the Upload object that this Part was added to.

object

string

The object type, which is always `upload.part`.

OBJECT The upload part object

```JSON
1
2
3
4
5
6
{
    "id": "part_def456",
    "object": "upload.part",
    "created_at": 1719186911,
    "upload_id": "upload_abc123"
}
```

## Images

Given a prompt and/or an input image, the model will generate a new image.
Related guide: [Image generation](https://platform.openai.com/docs/guides/images)

## Create image

posthttps://api.openai.com/v1/images/generations

Creates an image given a prompt.

### Request body

prompt

string

Required

A text description of the desired image(s). The maximum length is 1000 characters for `dall-e-2` and 4000 characters for `dall-e-3`.

model

string

Optional

Defaults to dall-e-2

The model to use for image generation.

n

integer or null

Optional

Defaults to 1

The number of images to generate. Must be between 1 and 10. For `dall-e-3`, only `n=1` is supported.

quality

string

Optional

Defaults to standard

The quality of the image that will be generated. `hd` creates images with finer details and greater consistency across the image. This param is only supported for `dall-e-3`.

response\_format

string or null

Optional

Defaults to url

The format in which the generated images are returned. Must be one of `url` or `b64_json`. URLs are only valid for 60 minutes after the image has been generated.

size

string or null

Optional

Defaults to 1024x1024

The size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`. Must be one of `1024x1024`, `1792x1024`, or `1024x1792` for `dall-e-3` models.

style

string or null

Optional

Defaults to vivid

The style of the generated images. Must be one of `vivid` or `natural`. Vivid causes the model to lean towards generating hyper-real and dramatic images. Natural causes the model to produce more natural, less hyper-real looking images. This param is only supported for `dall-e-3`.

user

string

Optional

A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

### Returns

Returns a list of [image](https://platform.openai.com/docs/api-reference/images/object) objects.

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
curl https://api.openai.com/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "dall-e-3",
    "prompt": "A cute baby sea otter",
    "n": 1,
    "size": "1024x1024"
  }'
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

client.images.generate(
  model="dall-e-3",
  prompt="A cute baby sea otter",
  n=1,
  size="1024x1024"
)
```

```javascript
1
2
3
4
5
6
7
8
9
10
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const image = await openai.images.generate({ model: "dall-e-3", prompt: "A cute baby sea otter" });

  console.log(image.data);
}
main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
{
  "created": 1589478378,
  "data": [\
    {\
      "url": "https://..."\
    },\
    {\
      "url": "https://..."\
    }\
  ]
}
```

## Create image edit

posthttps://api.openai.com/v1/images/edits

Creates an edited or extended image given an original image and a prompt.

### Request body

image

file

Required

The image to edit. Must be a valid PNG file, less than 4MB, and square. If mask is not provided, image must have transparency, which will be used as the mask.

prompt

string

Required

A text description of the desired image(s). The maximum length is 1000 characters.

mask

file

Optional

An additional image whose fully transparent areas (e.g. where alpha is zero) indicate where `image` should be edited. Must be a valid PNG file, less than 4MB, and have the same dimensions as `image`.

model

string

Optional

Defaults to dall-e-2

The model to use for image generation. Only `dall-e-2` is supported at this time.

n

integer or null

Optional

Defaults to 1

The number of images to generate. Must be between 1 and 10.

size

string or null

Optional

Defaults to 1024x1024

The size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024`.

response\_format

string or null

Optional

Defaults to url

The format in which the generated images are returned. Must be one of `url` or `b64_json`. URLs are only valid for 60 minutes after the image has been generated.

user

string

Optional

A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

### Returns

Returns a list of [image](https://platform.openai.com/docs/api-reference/images/object) objects.

Example request

curl

```bash
1
2
3
4
5
6
7
curl https://api.openai.com/v1/images/edits \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F image="@otter.png" \
  -F mask="@mask.png" \
  -F prompt="A cute baby sea otter wearing a beret" \
  -F n=2 \
  -F size="1024x1024"
```

```python
1
2
3
4
5
6
7
8
9
10
from openai import OpenAI
client = OpenAI()

client.images.edit(
  image=open("otter.png", "rb"),
  mask=open("mask.png", "rb"),
  prompt="A cute baby sea otter wearing a beret",
  n=2,
  size="1024x1024"
)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
import fs from "fs";
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const image = await openai.images.edit({
    image: fs.createReadStream("otter.png"),
    mask: fs.createReadStream("mask.png"),
    prompt: "A cute baby sea otter wearing a beret",
  });

  console.log(image.data);
}
main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
{
  "created": 1589478378,
  "data": [\
    {\
      "url": "https://..."\
    },\
    {\
      "url": "https://..."\
    }\
  ]
}
```

## Create image variation

posthttps://api.openai.com/v1/images/variations

Creates a variation of a given image.

### Request body

image

file

Required

The image to use as the basis for the variation(s). Must be a valid PNG file, less than 4MB, and square.

model

string

Optional

Defaults to dall-e-2

The model to use for image generation. Only `dall-e-2` is supported at this time.

n

integer or null

Optional

Defaults to 1

The number of images to generate. Must be between 1 and 10. For `dall-e-3`, only `n=1` is supported.

response\_format

string or null

Optional

Defaults to url

The format in which the generated images are returned. Must be one of `url` or `b64_json`. URLs are only valid for 60 minutes after the image has been generated.

size

string or null

Optional

Defaults to 1024x1024

The size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024`.

user

string

Optional

A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

### Returns

Returns a list of [image](https://platform.openai.com/docs/api-reference/images/object) objects.

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/images/variations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F image="@otter.png" \
  -F n=2 \
  -F size="1024x1024"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

response = client.images.create_variation(
  image=open("image_edit_original.png", "rb"),
  n=2,
  size="1024x1024"
)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import fs from "fs";
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const image = await openai.images.createVariation({
    image: fs.createReadStream("otter.png"),
  });

  console.log(image.data);
}
main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
{
  "created": 1589478378,
  "data": [\
    {\
      "url": "https://..."\
    },\
    {\
      "url": "https://..."\
    }\
  ]
}
```

## The image object

Represents the url or the content of an image generated by the OpenAI API.

b64\_json

string

The base64-encoded JSON of the generated image, if `response_format` is `b64_json`.

url

string

The URL of the generated image, if `response_format` is `url` (default).

revised\_prompt

string

The prompt that was used to generate the image, if there was any revision to the prompt.

OBJECT The image object

```JSON
1
2
3
4
{
  "url": "...",
  "revised_prompt": "..."
}
```

## Models

List and describe the various models available in the API. You can refer to the [Models](https://platform.openai.com/docs/models) documentation to understand what models are available and the differences between them.

## List models

gethttps://api.openai.com/v1/models

Lists the currently available models, and provides basic information about each one such as the owner and availability.

### Returns

A list of [model](https://platform.openai.com/docs/api-reference/models/object) objects.

Example request

curl

```bash
1
2
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

client.models.list()
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const list = await openai.models.list();

  for await (const model of list) {
    console.log(model);
  }
}
main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
{
  "object": "list",
  "data": [\
    {\
      "id": "model-id-0",\
      "object": "model",\
      "created": 1686935002,\
      "owned_by": "organization-owner"\
    },\
    {\
      "id": "model-id-1",\
      "object": "model",\
      "created": 1686935002,\
      "owned_by": "organization-owner",\
    },\
    {\
      "id": "model-id-2",\
      "object": "model",\
      "created": 1686935002,\
      "owned_by": "openai"\
    },\
  ],
  "object": "list"
}
```

## Retrieve model

gethttps://api.openai.com/v1/models/{model}

Retrieves a model instance, providing basic information about the model such as the owner and permissioning.

### Path parameters

model

string

Required

The ID of the model to use for this request

### Returns

The [model](https://platform.openai.com/docs/api-reference/models/object) object matching the specified ID.

Example request

gpt-4o

curl

```bash
1
2
curl https://api.openai.com/v1/models/gpt-4o \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

client.models.retrieve("gpt-4o")
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const model = await openai.models.retrieve("gpt-4o");

  console.log(model);
}

main();
```

Response

```json
1
2
3
4
5
6
{
  "id": "gpt-4o",
  "object": "model",
  "created": 1686935002,
  "owned_by": "openai"
}
```

## Delete a fine-tuned model

deletehttps://api.openai.com/v1/models/{model}

Delete a fine-tuned model. You must have the Owner role in your organization to delete a model.

### Path parameters

model

string

Required

The model to delete

### Returns

Deletion status.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/models/ft:gpt-4o-mini:acemeco:suffix:abc123 \
  -X DELETE \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

```python
1
2
3
4
from openai import OpenAI
client = OpenAI()

client.models.delete("ft:gpt-4o-mini:acemeco:suffix:abc123")
```

```javascript
1
2
3
4
5
6
7
8
9
10
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const model = await openai.models.del("ft:gpt-4o-mini:acemeco:suffix:abc123");

  console.log(model);
}
main();
```

Response

```json
1
2
3
4
5
{
  "id": "ft:gpt-4o-mini:acemeco:suffix:abc123",
  "object": "model",
  "deleted": true
}
```

## The model object

Describes an OpenAI model offering that can be used with the API.

id

string

The model identifier, which can be referenced in the API endpoints.

created

integer

The Unix timestamp (in seconds) when the model was created.

object

string

The object type, which is always "model".

owned\_by

string

The organization that owns the model.

OBJECT The model object

```JSON
1
2
3
4
5
6
{
  "id": "gpt-4o",
  "object": "model",
  "created": 1686935002,
  "owned_by": "openai"
}
```

## Moderations

Given text and/or image inputs, classifies if those inputs are potentially harmful across several categories.
Related guide: [Moderations](https://platform.openai.com/docs/guides/moderation)

## Create moderation

posthttps://api.openai.com/v1/moderations

Classifies if text and/or image inputs are potentially harmful. Learn
more in the [moderation guide](https://platform.openai.com/docs/guides/moderation).

### Request body

input

string or array

Required

Input (or inputs) to classify. Can be a single string, an array of strings, or
an array of multi-modal input objects similar to other models.

Show possible types

model

string

Optional

Defaults to omni-moderation-latest

The content moderation model you would like to use. Learn more in
[the moderation guide](https://platform.openai.com/docs/guides/moderation), and learn about
available models [here](https://platform.openai.com/docs/models#moderation).

### Returns

A [moderation](https://platform.openai.com/docs/api-reference/moderations/object) object.

Single stringSingle stringImage and textImage and text

Example request

curl

```bash
1
2
3
4
5
6
curl https://api.openai.com/v1/moderations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "input": "I want to kill them."
  }'
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

moderation = client.moderations.create(input="I want to kill them.")
print(moderation)
```

```javascript
1
2
3
4
5
6
7
8
9
10
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const moderation = await openai.moderations.create({ input: "I want to kill them." });

  console.log(moderation);
}
main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
{
  "id": "modr-AB8CjOTu2jiq12hp1AQPfeqFWaORR",
  "model": "text-moderation-007",
  "results": [\
    {\
      "flagged": true,\
      "categories": {\
        "sexual": false,\
        "hate": false,\
        "harassment": true,\
        "self-harm": false,\
        "sexual/minors": false,\
        "hate/threatening": false,\
        "violence/graphic": false,\
        "self-harm/intent": false,\
        "self-harm/instructions": false,\
        "harassment/threatening": true,\
        "violence": true\
      },\
      "category_scores": {\
        "sexual": 0.000011726012417057063,\
        "hate": 0.22706663608551025,\
        "harassment": 0.5215635299682617,\
        "self-harm": 2.227119921371923e-6,\
        "sexual/minors": 7.107352217872176e-8,\
        "hate/threatening": 0.023547329008579254,\
        "violence/graphic": 0.00003391829886822961,\
        "self-harm/intent": 1.646940972932498e-6,\
        "self-harm/instructions": 1.1198755256458526e-9,\
        "harassment/threatening": 0.5694745779037476,\
        "violence": 0.9971134662628174\
      }\
    }\
  ]
}
```

## The moderation object

Represents if a given text input is potentially harmful.

id

string

The unique identifier for the moderation request.

model

string

The model used to generate the moderation results.

results

array

A list of moderation objects.

Show properties

OBJECT The moderation object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
{
  "id": "modr-0d9740456c391e43c445bf0f010940c7",
  "model": "omni-moderation-latest",
  "results": [\
    {\
      "flagged": true,\
      "categories": {\
        "harassment": true,\
        "harassment/threatening": true,\
        "sexual": false,\
        "hate": false,\
        "hate/threatening": false,\
        "illicit": false,\
        "illicit/violent": false,\
        "self-harm/intent": false,\
        "self-harm/instructions": false,\
        "self-harm": false,\
        "sexual/minors": false,\
        "violence": true,\
        "violence/graphic": true\
      },\
      "category_scores": {\
        "harassment": 0.8189693396524255,\
        "harassment/threatening": 0.804985420696006,\
        "sexual": 1.573112165348997e-6,\
        "hate": 0.007562942636942845,\
        "hate/threatening": 0.004208854591835476,\
        "illicit": 0.030535955153511665,\
        "illicit/violent": 0.008925306722380033,\
        "self-harm/intent": 0.00023023930975076432,\
        "self-harm/instructions": 0.0002293869201073356,\
        "self-harm": 0.012598046106750154,\
        "sexual/minors": 2.212566909570261e-8,\
        "violence": 0.9999992735124786,\
        "violence/graphic": 0.843064871157054\
      },\
      "category_applied_input_types": {\
        "harassment": [\
          "text"\
        ],\
        "harassment/threatening": [\
          "text"\
        ],\
        "sexual": [\
          "text",\
          "image"\
        ],\
        "hate": [\
          "text"\
        ],\
        "hate/threatening": [\
          "text"\
        ],\
        "illicit": [\
          "text"\
        ],\
        "illicit/violent": [\
          "text"\
        ],\
        "self-harm/intent": [\
          "text",\
          "image"\
        ],\
        "self-harm/instructions": [\
          "text",\
          "image"\
        ],\
        "self-harm": [\
          "text",\
          "image"\
        ],\
        "sexual/minors": [\
          "text"\
        ],\
        "violence": [\
          "text",\
          "image"\
        ],\
        "violence/graphic": [\
          "text",\
          "image"\
        ]\
      }\
    }\
  ]
}
```

## Assistants  Beta

Build assistants that can call models and use tools to perform tasks.

[Get started with the Assistants API](https://platform.openai.com/docs/assistants)

## Create assistant  Beta

posthttps://api.openai.com/v1/assistants

Create an assistant with a model and instructions.

### Request body

model

string

Required

ID of the model to use. You can use the [List models](https://platform.openai.com/docs/api-reference/models/list) API to see all of your available models, or see our [Model overview](https://platform.openai.com/docs/models) for descriptions of them.

name

string or null

Optional

The name of the assistant. The maximum length is 256 characters.

description

string or null

Optional

The description of the assistant. The maximum length is 512 characters.

instructions

string or null

Optional

The system instructions that the assistant uses. The maximum length is 256,000 characters.

tools

array

Optional

Defaults to \[\]

A list of tool enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can be of types `code_interpreter`, `file_search`, or `function`.

Show possible types

tool\_resources

object or null

Optional

A set of resources that are used by the assistant's tools. The resources are specific to the type of tool. For example, the `code_interpreter` tool requires a list of file IDs, while the `file_search` tool requires a list of vector store IDs.

Show properties

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

temperature

number or null

Optional

Defaults to 1

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

top\_p

number or null

Optional

Defaults to 1

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

response\_format

"auto" or object

Optional

Specifies the format that the model must output. Compatible with [GPT-4o](https://platform.openai.com/docs/models#gpt-4o), [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4), and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

Show possible types

### Returns

An [assistant](https://platform.openai.com/docs/api-reference/assistants/object) object.

Code InterpreterCode InterpreterFilesFiles

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
10
curl "https://api.openai.com/v1/assistants" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{
    "instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
    "name": "Math Tutor",
    "tools": [{"type": "code_interpreter"}],
    "model": "gpt-4o"
  }'
```

```python
1
2
3
4
5
6
7
8
9
10
from openai import OpenAI
client = OpenAI()

my_assistant = client.beta.assistants.create(
    instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
    name="Math Tutor",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o",
)
print(my_assistant)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const myAssistant = await openai.beta.assistants.create({
    instructions:
      "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
    name: "Math Tutor",
    tools: [{ type: "code_interpreter" }],
    model: "gpt-4o",
  });

  console.log(myAssistant);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
{
  "id": "asst_abc123",
  "object": "assistant",
  "created_at": 1698984975,
  "name": "Math Tutor",
  "description": null,
  "model": "gpt-4o",
  "instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
  "tools": [\
    {\
      "type": "code_interpreter"\
    }\
  ],
  "metadata": {},
  "top_p": 1.0,
  "temperature": 1.0,
  "response_format": "auto"
}
```

## List assistants  Beta

gethttps://api.openai.com/v1/assistants

Returns a list of assistants.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

### Returns

A list of [assistant](https://platform.openai.com/docs/api-reference/assistants/object) objects.

Example request

curl

```bash
1
2
3
4
curl "https://api.openai.com/v1/assistants?order=desc&limit=20" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

my_assistants = client.beta.assistants.list(
    order="desc",
    limit="20",
)
print(my_assistants.data)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const myAssistants = await openai.beta.assistants.list({
    order: "desc",
    limit: "20",
  });

  console.log(myAssistants.data);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
{
  "object": "list",
  "data": [\
    {\
      "id": "asst_abc123",\
      "object": "assistant",\
      "created_at": 1698982736,\
      "name": "Coding Tutor",\
      "description": null,\
      "model": "gpt-4o",\
      "instructions": "You are a helpful assistant designed to make me better at coding!",\
      "tools": [],\
      "tool_resources": {},\
      "metadata": {},\
      "top_p": 1.0,\
      "temperature": 1.0,\
      "response_format": "auto"\
    },\
    {\
      "id": "asst_abc456",\
      "object": "assistant",\
      "created_at": 1698982718,\
      "name": "My Assistant",\
      "description": null,\
      "model": "gpt-4o",\
      "instructions": "You are a helpful assistant designed to make me better at coding!",\
      "tools": [],\
      "tool_resources": {},\
      "metadata": {},\
      "top_p": 1.0,\
      "temperature": 1.0,\
      "response_format": "auto"\
    },\
    {\
      "id": "asst_abc789",\
      "object": "assistant",\
      "created_at": 1698982643,\
      "name": null,\
      "description": null,\
      "model": "gpt-4o",\
      "instructions": null,\
      "tools": [],\
      "tool_resources": {},\
      "metadata": {},\
      "top_p": 1.0,\
      "temperature": 1.0,\
      "response_format": "auto"\
    }\
  ],
  "first_id": "asst_abc123",
  "last_id": "asst_abc789",
  "has_more": false
}
```

## Retrieve assistant  Beta

gethttps://api.openai.com/v1/assistants/{assistant\_id}

Retrieves an assistant.

### Path parameters

assistant\_id

string

Required

The ID of the assistant to retrieve.

### Returns

The [assistant](https://platform.openai.com/docs/api-reference/assistants/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/assistants/asst_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

my_assistant = client.beta.assistants.retrieve("asst_abc123")
print(my_assistant)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const myAssistant = await openai.beta.assistants.retrieve(
    "asst_abc123"
  );

  console.log(myAssistant);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
{
  "id": "asst_abc123",
  "object": "assistant",
  "created_at": 1699009709,
  "name": "HR Helper",
  "description": null,
  "model": "gpt-4o",
  "instructions": "You are an HR bot, and you have access to files to answer employee questions about company policies.",
  "tools": [\
    {\
      "type": "file_search"\
    }\
  ],
  "metadata": {},
  "top_p": 1.0,
  "temperature": 1.0,
  "response_format": "auto"
}
```

## Modify assistant  Beta

posthttps://api.openai.com/v1/assistants/{assistant\_id}

Modifies an assistant.

### Path parameters

assistant\_id

string

Required

The ID of the assistant to modify.

### Request body

model

Optional

ID of the model to use. You can use the [List models](https://platform.openai.com/docs/api-reference/models/list) API to see all of your available models, or see our [Model overview](https://platform.openai.com/docs/models) for descriptions of them.

name

string or null

Optional

The name of the assistant. The maximum length is 256 characters.

description

string or null

Optional

The description of the assistant. The maximum length is 512 characters.

instructions

string or null

Optional

The system instructions that the assistant uses. The maximum length is 256,000 characters.

tools

array

Optional

Defaults to \[\]

A list of tool enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can be of types `code_interpreter`, `file_search`, or `function`.

Show possible types

tool\_resources

object or null

Optional

A set of resources that are used by the assistant's tools. The resources are specific to the type of tool. For example, the `code_interpreter` tool requires a list of file IDs, while the `file_search` tool requires a list of vector store IDs.

Show properties

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

temperature

number or null

Optional

Defaults to 1

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

top\_p

number or null

Optional

Defaults to 1

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

response\_format

"auto" or object

Optional

Specifies the format that the model must output. Compatible with [GPT-4o](https://platform.openai.com/docs/models#gpt-4o), [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4), and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

Show possible types

### Returns

The modified [assistant](https://platform.openai.com/docs/api-reference/assistants/object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
curl https://api.openai.com/v1/assistants/asst_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{
      "instructions": "You are an HR bot, and you have access to files to answer employee questions about company policies. Always response with info from either of the files.",
      "tools": [{"type": "file_search"}],
      "model": "gpt-4o"
    }'
```

```python
1
2
3
4
5
6
7
8
9
10
11
12
from openai import OpenAI
client = OpenAI()

my_updated_assistant = client.beta.assistants.update(
  "asst_abc123",
  instructions="You are an HR bot, and you have access to files to answer employee questions about company policies. Always response with info from either of the files.",
  name="HR Helper",
  tools=[{"type": "file_search"}],
  model="gpt-4o"
)

print(my_updated_assistant)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const myUpdatedAssistant = await openai.beta.assistants.update(
    "asst_abc123",
    {
      instructions:
        "You are an HR bot, and you have access to files to answer employee questions about company policies. Always response with info from either of the files.",
      name: "HR Helper",
      tools: [{ type: "file_search" }],
      model: "gpt-4o"
    }
  );

  console.log(myUpdatedAssistant);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
{
  "id": "asst_123",
  "object": "assistant",
  "created_at": 1699009709,
  "name": "HR Helper",
  "description": null,
  "model": "gpt-4o",
  "instructions": "You are an HR bot, and you have access to files to answer employee questions about company policies. Always response with info from either of the files.",
  "tools": [\
    {\
      "type": "file_search"\
    }\
  ],
  "tool_resources": {
    "file_search": {
      "vector_store_ids": []
    }
  },
  "metadata": {},
  "top_p": 1.0,
  "temperature": 1.0,
  "response_format": "auto"
}
```

## Delete assistant  Beta

deletehttps://api.openai.com/v1/assistants/{assistant\_id}

Delete an assistant.

### Path parameters

assistant\_id

string

Required

The ID of the assistant to delete.

### Returns

Deletion status

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/assistants/asst_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2" \
  -X DELETE
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

response = client.beta.assistants.delete("asst_abc123")
print(response)
```

```javascript
1
2
3
4
5
6
7
8
9
10
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const response = await openai.beta.assistants.del("asst_abc123");

  console.log(response);
}
main();
```

Response

```json
1
2
3
4
5
{
  "id": "asst_abc123",
  "object": "assistant.deleted",
  "deleted": true
}
```

## The assistant object  Beta

Represents an `assistant` that can call the model and use tools.

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `assistant`.

created\_at

integer

The Unix timestamp (in seconds) for when the assistant was created.

name

string or null

The name of the assistant. The maximum length is 256 characters.

description

string or null

The description of the assistant. The maximum length is 512 characters.

model

string

ID of the model to use. You can use the [List models](https://platform.openai.com/docs/api-reference/models/list) API to see all of your available models, or see our [Model overview](https://platform.openai.com/docs/models) for descriptions of them.

instructions

string or null

The system instructions that the assistant uses. The maximum length is 256,000 characters.

tools

array

A list of tool enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can be of types `code_interpreter`, `file_search`, or `function`.

Show possible types

tool\_resources

object or null

A set of resources that are used by the assistant's tools. The resources are specific to the type of tool. For example, the `code_interpreter` tool requires a list of file IDs, while the `file_search` tool requires a list of vector store IDs.

Show properties

metadata

map

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

temperature

number or null

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

top\_p

number or null

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

response\_format

"auto" or object

Specifies the format that the model must output. Compatible with [GPT-4o](https://platform.openai.com/docs/models#gpt-4o), [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4), and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

Show possible types

OBJECT The assistant object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
{
  "id": "asst_abc123",
  "object": "assistant",
  "created_at": 1698984975,
  "name": "Math Tutor",
  "description": null,
  "model": "gpt-4o",
  "instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
  "tools": [\
    {\
      "type": "code_interpreter"\
    }\
  ],
  "metadata": {},
  "top_p": 1.0,
  "temperature": 1.0,
  "response_format": "auto"
}
```

## Threads  Beta

Create threads that assistants can interact with.

Related guide: [Assistants](https://platform.openai.com/docs/assistants/overview)

## Create thread  Beta

posthttps://api.openai.com/v1/threads

Create a thread.

### Request body

messages

array

Optional

A list of [messages](https://platform.openai.com/docs/api-reference/messages) to start the thread with.

Show properties

tool\_resources

object or null

Optional

A set of resources that are made available to the assistant's tools in this thread. The resources are specific to the type of tool. For example, the `code_interpreter` tool requires a list of file IDs, while the `file_search` tool requires a list of vector store IDs.

Show properties

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

### Returns

A [thread](https://platform.openai.com/docs/api-reference/threads) object.

EmptyEmptyMessagesMessages

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/threads \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2" \
  -d ''
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

empty_thread = client.beta.threads.create()
print(empty_thread)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const emptyThread = await openai.beta.threads.create();

  console.log(emptyThread);
}

main();
```

Response

```json
1
2
3
4
5
6
7
{
  "id": "thread_abc123",
  "object": "thread",
  "created_at": 1699012949,
  "metadata": {},
  "tool_resources": {}
}
```

## Retrieve thread  Beta

gethttps://api.openai.com/v1/threads/{thread\_id}

Retrieves a thread.

### Path parameters

thread\_id

string

Required

The ID of the thread to retrieve.

### Returns

The [thread](https://platform.openai.com/docs/api-reference/threads/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

my_thread = client.beta.threads.retrieve("thread_abc123")
print(my_thread)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const myThread = await openai.beta.threads.retrieve(
    "thread_abc123"
  );

  console.log(myThread);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
{
  "id": "thread_abc123",
  "object": "thread",
  "created_at": 1699014083,
  "metadata": {},
  "tool_resources": {
    "code_interpreter": {
      "file_ids": []
    }
  }
}
```

## Modify thread  Beta

posthttps://api.openai.com/v1/threads/{thread\_id}

Modifies a thread.

### Path parameters

thread\_id

string

Required

The ID of the thread to modify. Only the `metadata` can be modified.

### Request body

tool\_resources

object or null

Optional

A set of resources that are made available to the assistant's tools in this thread. The resources are specific to the type of tool. For example, the `code_interpreter` tool requires a list of file IDs, while the `file_search` tool requires a list of vector store IDs.

Show properties

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

### Returns

The modified [thread](https://platform.openai.com/docs/api-reference/threads/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
10
curl https://api.openai.com/v1/threads/thread_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{
      "metadata": {
        "modified": "true",
        "user": "abc123"
      }
    }'
```

```python
1
2
3
4
5
6
7
8
9
10
11
from openai import OpenAI
client = OpenAI()

my_updated_thread = client.beta.threads.update(
  "thread_abc123",
  metadata={
    "modified": "true",
    "user": "abc123"
  }
)
print(my_updated_thread)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const updatedThread = await openai.beta.threads.update(
    "thread_abc123",
    {
      metadata: { modified: "true", user: "abc123" },
    }
  );

  console.log(updatedThread);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
{
  "id": "thread_abc123",
  "object": "thread",
  "created_at": 1699014083,
  "metadata": {
    "modified": "true",
    "user": "abc123"
  },
  "tool_resources": {}
}
```

## Delete thread  Beta

deletehttps://api.openai.com/v1/threads/{thread\_id}

Delete a thread.

### Path parameters

thread\_id

string

Required

The ID of the thread to delete.

### Returns

Deletion status

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/threads/thread_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2" \
  -X DELETE
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

response = client.beta.threads.delete("thread_abc123")
print(response)
```

```javascript
1
2
3
4
5
6
7
8
9
10
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const response = await openai.beta.threads.del("thread_abc123");

  console.log(response);
}
main();
```

Response

```json
1
2
3
4
5
{
  "id": "thread_abc123",
  "object": "thread.deleted",
  "deleted": true
}
```

## The thread object  Beta

Represents a thread that contains [messages](https://platform.openai.com/docs/api-reference/messages).

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `thread`.

created\_at

integer

The Unix timestamp (in seconds) for when the thread was created.

tool\_resources

object or null

A set of resources that are made available to the assistant's tools in this thread. The resources are specific to the type of tool. For example, the `code_interpreter` tool requires a list of file IDs, while the `file_search` tool requires a list of vector store IDs.

Show properties

metadata

map

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

OBJECT The thread object

```JSON
1
2
3
4
5
6
{
  "id": "thread_abc123",
  "object": "thread",
  "created_at": 1698107661,
  "metadata": {}
}
```

## Messages  Beta

Create messages within threads

Related guide: [Assistants](https://platform.openai.com/docs/assistants/overview)

## Create message  Beta

posthttps://api.openai.com/v1/threads/{thread\_id}/messages

Create a message.

### Path parameters

thread\_id

string

Required

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads) to create a message for.

### Request body

role

string

Required

The role of the entity that is creating the message. Allowed values include:

- `user`: Indicates the message is sent by an actual user and should be used in most cases to represent user-generated messages.
- `assistant`: Indicates the message is generated by the assistant. Use this value to insert messages from the assistant into the conversation.

content

string or array

Required

Show possible types

attachments

array or null

Optional

A list of files attached to the message, and the tools they should be added to.

Show properties

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

### Returns

A [message](https://platform.openai.com/docs/api-reference/messages/object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
8
curl https://api.openai.com/v1/threads/thread_abc123/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{
      "role": "user",
      "content": "How does AI work? Explain it in simple terms."
    }'
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

thread_message = client.beta.threads.messages.create(
  "thread_abc123",
  role="user",
  content="How does AI work? Explain it in simple terms.",
)
print(thread_message)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const threadMessages = await openai.beta.threads.messages.create(
    "thread_abc123",
    { role: "user", content: "How does AI work? Explain it in simple terms." }
  );

  console.log(threadMessages);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "id": "msg_abc123",
  "object": "thread.message",
  "created_at": 1713226573,
  "assistant_id": null,
  "thread_id": "thread_abc123",
  "run_id": null,
  "role": "user",
  "content": [\
    {\
      "type": "text",\
      "text": {\
        "value": "How does AI work? Explain it in simple terms.",\
        "annotations": []\
      }\
    }\
  ],
  "attachments": [],
  "metadata": {}
}
```

## List messages  Beta

gethttps://api.openai.com/v1/threads/{thread\_id}/messages

Returns a list of messages for a given thread.

### Path parameters

thread\_id

string

Required

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads) the messages belong to.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

run\_id

string

Optional

Filter messages by the run ID that generated them.

### Returns

A list of [message](https://platform.openai.com/docs/api-reference/messages) objects.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

thread_messages = client.beta.threads.messages.list("thread_abc123")
print(thread_messages.data)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const threadMessages = await openai.beta.threads.messages.list(
    "thread_abc123"
  );

  console.log(threadMessages.data);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
{
  "object": "list",
  "data": [\
    {\
      "id": "msg_abc123",\
      "object": "thread.message",\
      "created_at": 1699016383,\
      "assistant_id": null,\
      "thread_id": "thread_abc123",\
      "run_id": null,\
      "role": "user",\
      "content": [\
        {\
          "type": "text",\
          "text": {\
            "value": "How does AI work? Explain it in simple terms.",\
            "annotations": []\
          }\
        }\
      ],\
      "attachments": [],\
      "metadata": {}\
    },\
    {\
      "id": "msg_abc456",\
      "object": "thread.message",\
      "created_at": 1699016383,\
      "assistant_id": null,\
      "thread_id": "thread_abc123",\
      "run_id": null,\
      "role": "user",\
      "content": [\
        {\
          "type": "text",\
          "text": {\
            "value": "Hello, what is AI?",\
            "annotations": []\
          }\
        }\
      ],\
      "attachments": [],\
      "metadata": {}\
    }\
  ],
  "first_id": "msg_abc123",
  "last_id": "msg_abc456",
  "has_more": false
}
```

## Retrieve message  Beta

gethttps://api.openai.com/v1/threads/{thread\_id}/messages/{message\_id}

Retrieve a message.

### Path parameters

thread\_id

string

Required

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads) to which this message belongs.

message\_id

string

Required

The ID of the message to retrieve.

### Returns

The [message](https://platform.openai.com/docs/api-reference/messages/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/messages/msg_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

message = client.beta.threads.messages.retrieve(
  message_id="msg_abc123",
  thread_id="thread_abc123",
)
print(message)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const message = await openai.beta.threads.messages.retrieve(
    "thread_abc123",
    "msg_abc123"
  );

  console.log(message);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "id": "msg_abc123",
  "object": "thread.message",
  "created_at": 1699017614,
  "assistant_id": null,
  "thread_id": "thread_abc123",
  "run_id": null,
  "role": "user",
  "content": [\
    {\
      "type": "text",\
      "text": {\
        "value": "How does AI work? Explain it in simple terms.",\
        "annotations": []\
      }\
    }\
  ],
  "attachments": [],
  "metadata": {}
}
```

## Modify message  Beta

posthttps://api.openai.com/v1/threads/{thread\_id}/messages/{message\_id}

Modifies a message.

### Path parameters

thread\_id

string

Required

The ID of the thread to which this message belongs.

message\_id

string

Required

The ID of the message to modify.

### Request body

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

### Returns

The modified [message](https://platform.openai.com/docs/api-reference/messages/object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
10
curl https://api.openai.com/v1/threads/thread_abc123/messages/msg_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{
      "metadata": {
        "modified": "true",
        "user": "abc123"
      }
    }'
```

```python
1
2
3
4
5
6
7
8
9
10
11
12
from openai import OpenAI
client = OpenAI()

message = client.beta.threads.messages.update(
  message_id="msg_abc12",
  thread_id="thread_abc123",
  metadata={
    "modified": "true",
    "user": "abc123",
  },
)
print(message)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const message = await openai.beta.threads.messages.update(
    "thread_abc123",
    "msg_abc123",
    {
      metadata: {
        modified: "true",
        user: "abc123",
      },
    }
  }'
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
{
  "id": "msg_abc123",
  "object": "thread.message",
  "created_at": 1699017614,
  "assistant_id": null,
  "thread_id": "thread_abc123",
  "run_id": null,
  "role": "user",
  "content": [\
    {\
      "type": "text",\
      "text": {\
        "value": "How does AI work? Explain it in simple terms.",\
        "annotations": []\
      }\
    }\
  ],
  "file_ids": [],
  "metadata": {
    "modified": "true",
    "user": "abc123"
  }
}
```

## Delete message  Beta

deletehttps://api.openai.com/v1/threads/{thread\_id}/messages/{message\_id}

Deletes a message.

### Path parameters

thread\_id

string

Required

The ID of the thread to which this message belongs.

message\_id

string

Required

The ID of the message to delete.

### Returns

Deletion status

Example request

curl

```bash
1
2
3
4
curl -X DELETE https://api.openai.com/v1/threads/thread_abc123/messages/msg_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

deleted_message = client.beta.threads.messages.delete(
  message_id="msg_abc12",
  thread_id="thread_abc123",
)
print(deleted_message)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const deletedMessage = await openai.beta.threads.messages.del(
    "thread_abc123",
    "msg_abc123"
  );

  console.log(deletedMessage);
}
```

Response

```json
1
2
3
4
5
{
  "id": "msg_abc123",
  "object": "thread.message.deleted",
  "deleted": true
}
```

## The message object  Beta

Represents a message within a [thread](https://platform.openai.com/docs/api-reference/threads).

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `thread.message`.

created\_at

integer

The Unix timestamp (in seconds) for when the message was created.

thread\_id

string

The [thread](https://platform.openai.com/docs/api-reference/threads) ID that this message belongs to.

status

string

The status of the message, which can be either `in_progress`, `incomplete`, or `completed`.

incomplete\_details

object or null

On an incomplete message, details about why the message is incomplete.

Show properties

completed\_at

integer or null

The Unix timestamp (in seconds) for when the message was completed.

incomplete\_at

integer or null

The Unix timestamp (in seconds) for when the message was marked as incomplete.

role

string

The entity that produced the message. One of `user` or `assistant`.

content

array

The content of the message in array of text and/or images.

Show possible types

assistant\_id

string or null

If applicable, the ID of the [assistant](https://platform.openai.com/docs/api-reference/assistants) that authored this message.

run\_id

string or null

The ID of the [run](https://platform.openai.com/docs/api-reference/runs) associated with the creation of this message. Value is `null` when messages are created manually using the create message or create thread endpoints.

attachments

array or null

A list of files attached to the message, and the tools they were added to.

Show properties

metadata

map

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

OBJECT The message object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "id": "msg_abc123",
  "object": "thread.message",
  "created_at": 1698983503,
  "thread_id": "thread_abc123",
  "role": "assistant",
  "content": [\
    {\
      "type": "text",\
      "text": {\
        "value": "Hi! How can I help you today?",\
        "annotations": []\
      }\
    }\
  ],
  "assistant_id": "asst_abc123",
  "run_id": "run_abc123",
  "attachments": [],
  "metadata": {}
}
```

## Runs  Beta

Represents an execution run on a thread.

Related guide: [Assistants](https://platform.openai.com/docs/assistants/overview)

## Create run  Beta

posthttps://api.openai.com/v1/threads/{thread\_id}/runs

Create a run.

### Path parameters

thread\_id

string

Required

The ID of the thread to run.

### Query parameters

include\[\]

array

Optional

A list of additional fields to include in the response. Currently the only supported value is `step_details.tool_calls[*].file_search.results[*].content` to fetch the file search result content.

See the [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search#customizing-file-search-settings) for more information.

### Request body

assistant\_id

string

Required

The ID of the [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to execute this run.

model

string

Optional

The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to be used to execute this run. If a value is provided here, it will override the model associated with the assistant. If not, the model associated with the assistant will be used.

instructions

string or null

Optional

Overrides the [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant) of the assistant. This is useful for modifying the behavior on a per-run basis.

additional\_instructions

string or null

Optional

Appends additional instructions at the end of the instructions for the run. This is useful for modifying the behavior on a per-run basis without overriding other instructions.

additional\_messages

array or null

Optional

Adds additional messages to the thread before creating the run.

Show properties

tools

array or null

Optional

Override the tools the assistant can use for this run. This is useful for modifying the behavior on a per-run basis.

Show possible types

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

temperature

number or null

Optional

Defaults to 1

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

top\_p

number or null

Optional

Defaults to 1

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

stream

boolean or null

Optional

If `true`, returns a stream of events that happen during the Run as server-sent events, terminating when the Run enters a terminal state with a `data: [DONE]` message.

max\_prompt\_tokens

integer or null

Optional

The maximum number of prompt tokens that may be used over the course of the run. The run will make a best effort to use only the number of prompt tokens specified, across multiple turns of the run. If the run exceeds the number of prompt tokens specified, the run will end with status `incomplete`. See `incomplete_details` for more info.

max\_completion\_tokens

integer or null

Optional

The maximum number of completion tokens that may be used over the course of the run. The run will make a best effort to use only the number of completion tokens specified, across multiple turns of the run. If the run exceeds the number of completion tokens specified, the run will end with status `incomplete`. See `incomplete_details` for more info.

truncation\_strategy

object

Optional

Controls for how a thread will be truncated prior to the run. Use this to control the intial context window of the run.

Show properties

tool\_choice

string or object

Optional

Controls which (if any) tool is called by the model.
`none` means the model will not call any tools and instead generates a message.
`auto` is the default value and means the model can pick between generating a message or calling one or more tools.
`required` means the model must call one or more tools before responding to the user.
Specifying a particular tool like `{"type": "file_search"}` or `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool.

Show possible types

parallel\_tool\_calls

boolean

Optional

Defaults to true

Whether to enable [parallel function calling](https://platform.openai.com/docs/guides/function-calling#configuring-parallel-function-calling) during tool use.

response\_format

"auto" or object

Optional

Specifies the format that the model must output. Compatible with [GPT-4o](https://platform.openai.com/docs/models#gpt-4o), [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4), and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

Show possible types

### Returns

A [run](https://platform.openai.com/docs/api-reference/runs/object) object.

DefaultDefaultStreamingStreamingStreaming with FunctionsStreaming with Functions

Example request

curl

```bash
1
2
3
4
5
6
7
curl https://api.openai.com/v1/threads/thread_abc123/runs \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{
    "assistant_id": "asst_abc123"
  }'
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

run = client.beta.threads.runs.create(
  thread_id="thread_abc123",
  assistant_id="asst_abc123"
)

print(run)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const run = await openai.beta.threads.runs.create(
    "thread_abc123",
    { assistant_id: "asst_abc123" }
  );

  console.log(run);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
{
  "id": "run_abc123",
  "object": "thread.run",
  "created_at": 1699063290,
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "status": "queued",
  "started_at": 1699063290,
  "expires_at": null,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": 1699063291,
  "last_error": null,
  "model": "gpt-4o",
  "instructions": null,
  "incomplete_details": null,
  "tools": [\
    {\
      "type": "code_interpreter"\
    }\
  ],
  "metadata": {},
  "usage": null,
  "temperature": 1.0,
  "top_p": 1.0,
  "max_prompt_tokens": 1000,
  "max_completion_tokens": 1000,
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "response_format": "auto",
  "tool_choice": "auto",
  "parallel_tool_calls": true
}
```

## Create thread and run  Beta

posthttps://api.openai.com/v1/threads/runs

Create a thread and run it in one request.

### Request body

assistant\_id

string

Required

The ID of the [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to execute this run.

thread

object

Optional

Options to create a new thread. If no thread is provided when running a
request, an empty thread will be created.

Show properties

model

string

Optional

The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to be used to execute this run. If a value is provided here, it will override the model associated with the assistant. If not, the model associated with the assistant will be used.

instructions

string or null

Optional

Override the default system message of the assistant. This is useful for modifying the behavior on a per-run basis.

tools

array or null

Optional

Override the tools the assistant can use for this run. This is useful for modifying the behavior on a per-run basis.

tool\_resources

object or null

Optional

A set of resources that are used by the assistant's tools. The resources are specific to the type of tool. For example, the `code_interpreter` tool requires a list of file IDs, while the `file_search` tool requires a list of vector store IDs.

Show properties

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

temperature

number or null

Optional

Defaults to 1

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

top\_p

number or null

Optional

Defaults to 1

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

stream

boolean or null

Optional

If `true`, returns a stream of events that happen during the Run as server-sent events, terminating when the Run enters a terminal state with a `data: [DONE]` message.

max\_prompt\_tokens

integer or null

Optional

The maximum number of prompt tokens that may be used over the course of the run. The run will make a best effort to use only the number of prompt tokens specified, across multiple turns of the run. If the run exceeds the number of prompt tokens specified, the run will end with status `incomplete`. See `incomplete_details` for more info.

max\_completion\_tokens

integer or null

Optional

The maximum number of completion tokens that may be used over the course of the run. The run will make a best effort to use only the number of completion tokens specified, across multiple turns of the run. If the run exceeds the number of completion tokens specified, the run will end with status `incomplete`. See `incomplete_details` for more info.

truncation\_strategy

object

Optional

Controls for how a thread will be truncated prior to the run. Use this to control the intial context window of the run.

Show properties

tool\_choice

string or object

Optional

Controls which (if any) tool is called by the model.
`none` means the model will not call any tools and instead generates a message.
`auto` is the default value and means the model can pick between generating a message or calling one or more tools.
`required` means the model must call one or more tools before responding to the user.
Specifying a particular tool like `{"type": "file_search"}` or `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool.

Show possible types

parallel\_tool\_calls

boolean

Optional

Defaults to true

Whether to enable [parallel function calling](https://platform.openai.com/docs/guides/function-calling#configuring-parallel-function-calling) during tool use.

response\_format

"auto" or object

Optional

Specifies the format that the model must output. Compatible with [GPT-4o](https://platform.openai.com/docs/models#gpt-4o), [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4), and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

Show possible types

### Returns

A [run](https://platform.openai.com/docs/api-reference/runs/object) object.

DefaultDefaultStreamingStreamingStreaming with FunctionsStreaming with Functions

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
10
11
12
curl https://api.openai.com/v1/threads/runs \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{
      "assistant_id": "asst_abc123",
      "thread": {
        "messages": [\
          {"role": "user", "content": "Explain deep learning to a 5 year old."}\
        ]
      }
    }'
```

```python
1
2
3
4
5
6
7
8
9
10
11
12
13
from openai import OpenAI
client = OpenAI()

run = client.beta.threads.create_and_run(
  assistant_id="asst_abc123",
  thread={
    "messages": [\
      {"role": "user", "content": "Explain deep learning to a 5 year old."}\
    ]
  }
)

print(run)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const run = await openai.beta.threads.createAndRun({
    assistant_id: "asst_abc123",
    thread: {
      messages: [\
        { role: "user", content: "Explain deep learning to a 5 year old." },\
      ],
    },
  });

  console.log(run);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
{
  "id": "run_abc123",
  "object": "thread.run",
  "created_at": 1699076792,
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "status": "queued",
  "started_at": null,
  "expires_at": 1699077392,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": null,
  "required_action": null,
  "last_error": null,
  "model": "gpt-4o",
  "instructions": "You are a helpful assistant.",
  "tools": [],
  "tool_resources": {},
  "metadata": {},
  "temperature": 1.0,
  "top_p": 1.0,
  "max_completion_tokens": null,
  "max_prompt_tokens": null,
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "incomplete_details": null,
  "usage": null,
  "response_format": "auto",
  "tool_choice": "auto",
  "parallel_tool_calls": true
}
```

## List runs  Beta

gethttps://api.openai.com/v1/threads/{thread\_id}/runs

Returns a list of runs belonging to a thread.

### Path parameters

thread\_id

string

Required

The ID of the thread the run belongs to.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

### Returns

A list of [run](https://platform.openai.com/docs/api-reference/runs/object) objects.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/runs \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

runs = client.beta.threads.runs.list(
  "thread_abc123"
)

print(runs)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const runs = await openai.beta.threads.runs.list(
    "thread_abc123"
  );

  console.log(runs);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
{
  "object": "list",
  "data": [\
    {\
      "id": "run_abc123",\
      "object": "thread.run",\
      "created_at": 1699075072,\
      "assistant_id": "asst_abc123",\
      "thread_id": "thread_abc123",\
      "status": "completed",\
      "started_at": 1699075072,\
      "expires_at": null,\
      "cancelled_at": null,\
      "failed_at": null,\
      "completed_at": 1699075073,\
      "last_error": null,\
      "model": "gpt-4o",\
      "instructions": null,\
      "incomplete_details": null,\
      "tools": [\
        {\
          "type": "code_interpreter"\
        }\
      ],\
      "tool_resources": {\
        "code_interpreter": {\
          "file_ids": [\
            "file-abc123",\
            "file-abc456"\
          ]\
        }\
      },\
      "metadata": {},\
      "usage": {\
        "prompt_tokens": 123,\
        "completion_tokens": 456,\
        "total_tokens": 579\
      },\
      "temperature": 1.0,\
      "top_p": 1.0,\
      "max_prompt_tokens": 1000,\
      "max_completion_tokens": 1000,\
      "truncation_strategy": {\
        "type": "auto",\
        "last_messages": null\
      },\
      "response_format": "auto",\
      "tool_choice": "auto",\
      "parallel_tool_calls": true\
    },\
    {\
      "id": "run_abc456",\
      "object": "thread.run",\
      "created_at": 1699063290,\
      "assistant_id": "asst_abc123",\
      "thread_id": "thread_abc123",\
      "status": "completed",\
      "started_at": 1699063290,\
      "expires_at": null,\
      "cancelled_at": null,\
      "failed_at": null,\
      "completed_at": 1699063291,\
      "last_error": null,\
      "model": "gpt-4o",\
      "instructions": null,\
      "incomplete_details": null,\
      "tools": [\
        {\
          "type": "code_interpreter"\
        }\
      ],\
      "tool_resources": {\
        "code_interpreter": {\
          "file_ids": [\
            "file-abc123",\
            "file-abc456"\
          ]\
        }\
      },\
      "metadata": {},\
      "usage": {\
        "prompt_tokens": 123,\
        "completion_tokens": 456,\
        "total_tokens": 579\
      },\
      "temperature": 1.0,\
      "top_p": 1.0,\
      "max_prompt_tokens": 1000,\
      "max_completion_tokens": 1000,\
      "truncation_strategy": {\
        "type": "auto",\
        "last_messages": null\
      },\
      "response_format": "auto",\
      "tool_choice": "auto",\
      "parallel_tool_calls": true\
    }\
  ],
  "first_id": "run_abc123",
  "last_id": "run_abc456",
  "has_more": false
}
```

## Retrieve run  Beta

gethttps://api.openai.com/v1/threads/{thread\_id}/runs/{run\_id}

Retrieves a run.

### Path parameters

thread\_id

string

Required

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads) that was run.

run\_id

string

Required

The ID of the run to retrieve.

### Returns

The [run](https://platform.openai.com/docs/api-reference/runs/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

run = client.beta.threads.runs.retrieve(
  thread_id="thread_abc123",
  run_id="run_abc123"
)

print(run)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const run = await openai.beta.threads.runs.retrieve(
    "thread_abc123",
    "run_abc123"
  );

  console.log(run);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
{
  "id": "run_abc123",
  "object": "thread.run",
  "created_at": 1699075072,
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "status": "completed",
  "started_at": 1699075072,
  "expires_at": null,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": 1699075073,
  "last_error": null,
  "model": "gpt-4o",
  "instructions": null,
  "incomplete_details": null,
  "tools": [\
    {\
      "type": "code_interpreter"\
    }\
  ],
  "metadata": {},
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  },
  "temperature": 1.0,
  "top_p": 1.0,
  "max_prompt_tokens": 1000,
  "max_completion_tokens": 1000,
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "response_format": "auto",
  "tool_choice": "auto",
  "parallel_tool_calls": true
}
```

## Modify run  Beta

posthttps://api.openai.com/v1/threads/{thread\_id}/runs/{run\_id}

Modifies a run.

### Path parameters

thread\_id

string

Required

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads) that was run.

run\_id

string

Required

The ID of the run to modify.

### Request body

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

### Returns

The modified [run](https://platform.openai.com/docs/api-reference/runs/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{
    "metadata": {
      "user_id": "user_abc123"
    }
  }'
```

```python
1
2
3
4
5
6
7
8
9
10
from openai import OpenAI
client = OpenAI()

run = client.beta.threads.runs.update(
  thread_id="thread_abc123",
  run_id="run_abc123",
  metadata={"user_id": "user_abc123"},
)

print(run)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const run = await openai.beta.threads.runs.update(
    "thread_abc123",
    "run_abc123",
    {
      metadata: {
        user_id: "user_abc123",
      },
    }
  );

  console.log(run);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
{
  "id": "run_abc123",
  "object": "thread.run",
  "created_at": 1699075072,
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "status": "completed",
  "started_at": 1699075072,
  "expires_at": null,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": 1699075073,
  "last_error": null,
  "model": "gpt-4o",
  "instructions": null,
  "incomplete_details": null,
  "tools": [\
    {\
      "type": "code_interpreter"\
    }\
  ],
  "tool_resources": {
    "code_interpreter": {
      "file_ids": [\
        "file-abc123",\
        "file-abc456"\
      ]
    }
  },
  "metadata": {
    "user_id": "user_abc123"
  },
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  },
  "temperature": 1.0,
  "top_p": 1.0,
  "max_prompt_tokens": 1000,
  "max_completion_tokens": 1000,
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "response_format": "auto",
  "tool_choice": "auto",
  "parallel_tool_calls": true
}
```

## Submit tool outputs to run  Beta

posthttps://api.openai.com/v1/threads/{thread\_id}/runs/{run\_id}/submit\_tool\_outputs

When a run has the `status: "requires_action"` and `required_action.type` is `submit_tool_outputs`, this endpoint can be used to submit the outputs from the tool calls once they're all completed. All outputs must be submitted in a single request.

### Path parameters

thread\_id

string

Required

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads) to which this run belongs.

run\_id

string

Required

The ID of the run that requires the tool output submission.

### Request body

tool\_outputs

array

Required

A list of tools for which the outputs are being submitted.

Show properties

stream

boolean or null

Optional

If `true`, returns a stream of events that happen during the Run as server-sent events, terminating when the Run enters a terminal state with a `data: [DONE]` message.

### Returns

The modified [run](https://platform.openai.com/docs/api-reference/runs/object) object matching the specified ID.

DefaultDefaultStreamingStreaming

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
10
11
12
curl https://api.openai.com/v1/threads/thread_123/runs/run_123/submit_tool_outputs \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{
    "tool_outputs": [\
      {\
        "tool_call_id": "call_001",\
        "output": "70 degrees and sunny."\
      }\
    ]
  }'
```

```python
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
from openai import OpenAI
client = OpenAI()

run = client.beta.threads.runs.submit_tool_outputs(
  thread_id="thread_123",
  run_id="run_123",
  tool_outputs=[\
    {\
      "tool_call_id": "call_001",\
      "output": "70 degrees and sunny."\
    }\
  ]
)

print(run)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const run = await openai.beta.threads.runs.submitToolOutputs(
    "thread_123",
    "run_123",
    {
      tool_outputs: [\
        {\
          tool_call_id: "call_001",\
          output: "70 degrees and sunny.",\
        },\
      ],
    }
  );

  console.log(run);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
{
  "id": "run_123",
  "object": "thread.run",
  "created_at": 1699075592,
  "assistant_id": "asst_123",
  "thread_id": "thread_123",
  "status": "queued",
  "started_at": 1699075592,
  "expires_at": 1699076192,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": null,
  "last_error": null,
  "model": "gpt-4o",
  "instructions": null,
  "tools": [\
    {\
      "type": "function",\
      "function": {\
        "name": "get_current_weather",\
        "description": "Get the current weather in a given location",\
        "parameters": {\
          "type": "object",\
          "properties": {\
            "location": {\
              "type": "string",\
              "description": "The city and state, e.g. San Francisco, CA"\
            },\
            "unit": {\
              "type": "string",\
              "enum": ["celsius", "fahrenheit"]\
            }\
          },\
          "required": ["location"]\
        }\
      }\
    }\
  ],
  "metadata": {},
  "usage": null,
  "temperature": 1.0,
  "top_p": 1.0,
  "max_prompt_tokens": 1000,
  "max_completion_tokens": 1000,
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "response_format": "auto",
  "tool_choice": "auto",
  "parallel_tool_calls": true
}
```

## Cancel a run  Beta

posthttps://api.openai.com/v1/threads/{thread\_id}/runs/{run\_id}/cancel

Cancels a run that is `in_progress`.

### Path parameters

thread\_id

string

Required

The ID of the thread to which this run belongs.

run\_id

string

Required

The ID of the run to cancel.

### Returns

The modified [run](https://platform.openai.com/docs/api-reference/runs/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123/cancel \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2" \
  -X POST
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

run = client.beta.threads.runs.cancel(
  thread_id="thread_abc123",
  run_id="run_abc123"
)

print(run)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const run = await openai.beta.threads.runs.cancel(
    "thread_abc123",
    "run_abc123"
  );

  console.log(run);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
{
  "id": "run_abc123",
  "object": "thread.run",
  "created_at": 1699076126,
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "status": "cancelling",
  "started_at": 1699076126,
  "expires_at": 1699076726,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": null,
  "last_error": null,
  "model": "gpt-4o",
  "instructions": "You summarize books.",
  "tools": [\
    {\
      "type": "file_search"\
    }\
  ],
  "tool_resources": {
    "file_search": {
      "vector_store_ids": ["vs_123"]
    }
  },
  "metadata": {},
  "usage": null,
  "temperature": 1.0,
  "top_p": 1.0,
  "response_format": "auto",
  "tool_choice": "auto",
  "parallel_tool_calls": true
}
```

## The run object  Beta

Represents an execution run on a [thread](https://platform.openai.com/docs/api-reference/threads).

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `thread.run`.

created\_at

integer

The Unix timestamp (in seconds) for when the run was created.

thread\_id

string

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads) that was executed on as a part of this run.

assistant\_id

string

The ID of the [assistant](https://platform.openai.com/docs/api-reference/assistants) used for execution of this run.

status

string

The status of the run, which can be either `queued`, `in_progress`, `requires_action`, `cancelling`, `cancelled`, `failed`, `completed`, `incomplete`, or `expired`.

required\_action

object or null

Details on the action required to continue the run. Will be `null` if no action is required.

Show properties

last\_error

object or null

The last error associated with this run. Will be `null` if there are no errors.

Show properties

expires\_at

integer or null

The Unix timestamp (in seconds) for when the run will expire.

started\_at

integer or null

The Unix timestamp (in seconds) for when the run was started.

cancelled\_at

integer or null

The Unix timestamp (in seconds) for when the run was cancelled.

failed\_at

integer or null

The Unix timestamp (in seconds) for when the run failed.

completed\_at

integer or null

The Unix timestamp (in seconds) for when the run was completed.

incomplete\_details

object or null

Details on why the run is incomplete. Will be `null` if the run is not incomplete.

Show properties

model

string

The model that the [assistant](https://platform.openai.com/docs/api-reference/assistants) used for this run.

instructions

string

The instructions that the [assistant](https://platform.openai.com/docs/api-reference/assistants) used for this run.

tools

array

The list of tools that the [assistant](https://platform.openai.com/docs/api-reference/assistants) used for this run.

Show possible types

metadata

map

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

usage

object or null

Usage statistics related to the run. This value will be `null` if the run is not in a terminal state (i.e. `in_progress`, `queued`, etc.).

Show properties

temperature

number or null

The sampling temperature used for this run. If not set, defaults to 1.

top\_p

number or null

The nucleus sampling value used for this run. If not set, defaults to 1.

max\_prompt\_tokens

integer or null

The maximum number of prompt tokens specified to have been used over the course of the run.

max\_completion\_tokens

integer or null

The maximum number of completion tokens specified to have been used over the course of the run.

truncation\_strategy

object

Controls for how a thread will be truncated prior to the run. Use this to control the intial context window of the run.

Show properties

tool\_choice

string or object

Controls which (if any) tool is called by the model.
`none` means the model will not call any tools and instead generates a message.
`auto` is the default value and means the model can pick between generating a message or calling one or more tools.
`required` means the model must call one or more tools before responding to the user.
Specifying a particular tool like `{"type": "file_search"}` or `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool.

Show possible types

parallel\_tool\_calls

boolean

Whether to enable [parallel function calling](https://platform.openai.com/docs/guides/function-calling#configuring-parallel-function-calling) during tool use.

response\_format

"auto" or object

Specifies the format that the model must output. Compatible with [GPT-4o](https://platform.openai.com/docs/models#gpt-4o), [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4), and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

Show possible types

OBJECT The run object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
{
  "id": "run_abc123",
  "object": "thread.run",
  "created_at": 1698107661,
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "status": "completed",
  "started_at": 1699073476,
  "expires_at": null,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": 1699073498,
  "last_error": null,
  "model": "gpt-4o",
  "instructions": null,
  "tools": [{"type": "file_search"}, {"type": "code_interpreter"}],
  "metadata": {},
  "incomplete_details": null,
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  },
  "temperature": 1.0,
  "top_p": 1.0,
  "max_prompt_tokens": 1000,
  "max_completion_tokens": 1000,
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "response_format": "auto",
  "tool_choice": "auto",
  "parallel_tool_calls": true
}
```

## Run steps  Beta

Represents the steps (model and tool calls) taken during the run.

Related guide: [Assistants](https://platform.openai.com/docs/assistants/overview)

## List run steps  Beta

gethttps://api.openai.com/v1/threads/{thread\_id}/runs/{run\_id}/steps

Returns a list of run steps belonging to a run.

### Path parameters

thread\_id

string

Required

The ID of the thread the run and run steps belong to.

run\_id

string

Required

The ID of the run the run steps belong to.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

include\[\]

array

Optional

A list of additional fields to include in the response. Currently the only supported value is `step_details.tool_calls[*].file_search.results[*].content` to fetch the file search result content.

See the [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search#customizing-file-search-settings) for more information.

### Returns

A list of [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object) objects.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123/steps \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

run_steps = client.beta.threads.runs.steps.list(
    thread_id="thread_abc123",
    run_id="run_abc123"
)

print(run_steps)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const runStep = await openai.beta.threads.runs.steps.list(
    "thread_abc123",
    "run_abc123"
  );
  console.log(runStep);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
{
  "object": "list",
  "data": [\
    {\
      "id": "step_abc123",\
      "object": "thread.run.step",\
      "created_at": 1699063291,\
      "run_id": "run_abc123",\
      "assistant_id": "asst_abc123",\
      "thread_id": "thread_abc123",\
      "type": "message_creation",\
      "status": "completed",\
      "cancelled_at": null,\
      "completed_at": 1699063291,\
      "expired_at": null,\
      "failed_at": null,\
      "last_error": null,\
      "step_details": {\
        "type": "message_creation",\
        "message_creation": {\
          "message_id": "msg_abc123"\
        }\
      },\
      "usage": {\
        "prompt_tokens": 123,\
        "completion_tokens": 456,\
        "total_tokens": 579\
      }\
    }\
  ],
  "first_id": "step_abc123",
  "last_id": "step_abc456",
  "has_more": false
}
```

## Retrieve run step  Beta

gethttps://api.openai.com/v1/threads/{thread\_id}/runs/{run\_id}/steps/{step\_id}

Retrieves a run step.

### Path parameters

thread\_id

string

Required

The ID of the thread to which the run and run step belongs.

run\_id

string

Required

The ID of the run to which the run step belongs.

step\_id

string

Required

The ID of the run step to retrieve.

### Query parameters

include\[\]

array

Optional

A list of additional fields to include in the response. Currently the only supported value is `step_details.tool_calls[*].file_search.results[*].content` to fetch the file search result content.

See the [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search#customizing-file-search-settings) for more information.

### Returns

The [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123/steps/step_abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
6
7
8
9
10
from openai import OpenAI
client = OpenAI()

run_step = client.beta.threads.runs.steps.retrieve(
    thread_id="thread_abc123",
    run_id="run_abc123",
    step_id="step_abc123"
)

print(run_step)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const runStep = await openai.beta.threads.runs.steps.retrieve(
    "thread_abc123",
    "run_abc123",
    "step_abc123"
  );
  console.log(runStep);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
{
  "id": "step_abc123",
  "object": "thread.run.step",
  "created_at": 1699063291,
  "run_id": "run_abc123",
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "type": "message_creation",
  "status": "completed",
  "cancelled_at": null,
  "completed_at": 1699063291,
  "expired_at": null,
  "failed_at": null,
  "last_error": null,
  "step_details": {
    "type": "message_creation",
    "message_creation": {
      "message_id": "msg_abc123"
    }
  },
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  }
}
```

## The run step object  Beta

Represents a step in execution of a run.

id

string

The identifier of the run step, which can be referenced in API endpoints.

object

string

The object type, which is always `thread.run.step`.

created\_at

integer

The Unix timestamp (in seconds) for when the run step was created.

assistant\_id

string

The ID of the [assistant](https://platform.openai.com/docs/api-reference/assistants) associated with the run step.

thread\_id

string

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads) that was run.

run\_id

string

The ID of the [run](https://platform.openai.com/docs/api-reference/runs) that this run step is a part of.

type

string

The type of run step, which can be either `message_creation` or `tool_calls`.

status

string

The status of the run step, which can be either `in_progress`, `cancelled`, `failed`, `completed`, or `expired`.

step\_details

object

The details of the run step.

Show possible types

last\_error

object or null

The last error associated with this run step. Will be `null` if there are no errors.

Show properties

expired\_at

integer or null

The Unix timestamp (in seconds) for when the run step expired. A step is considered expired if the parent run is expired.

cancelled\_at

integer or null

The Unix timestamp (in seconds) for when the run step was cancelled.

failed\_at

integer or null

The Unix timestamp (in seconds) for when the run step failed.

completed\_at

integer or null

The Unix timestamp (in seconds) for when the run step completed.

metadata

map

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

usage

object or null

Usage statistics related to the run step. This value will be `null` while the run step's status is `in_progress`.

Show properties

OBJECT The run step object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
{
  "id": "step_abc123",
  "object": "thread.run.step",
  "created_at": 1699063291,
  "run_id": "run_abc123",
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "type": "message_creation",
  "status": "completed",
  "cancelled_at": null,
  "completed_at": 1699063291,
  "expired_at": null,
  "failed_at": null,
  "last_error": null,
  "step_details": {
    "type": "message_creation",
    "message_creation": {
      "message_id": "msg_abc123"
    }
  },
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  }
}
```

## Vector stores  Beta

Vector stores are used to store files for use by the `file_search` tool.

Related guide: [File Search](https://platform.openai.com/docs/assistants/tools/file-search)

## Create vector store  Beta

posthttps://api.openai.com/v1/vector\_stores

Create a vector store.

### Request body

file\_ids

array

Optional

A list of [File](https://platform.openai.com/docs/api-reference/files) IDs that the vector store should use. Useful for tools like `file_search` that can access files.

name

string

Optional

The name of the vector store.

expires\_after

object

Optional

The expiration policy for a vector store.

Show properties

chunking\_strategy

object

Optional

The chunking strategy used to chunk the file(s). If not set, will use the `auto` strategy. Only applicable if `file_ids` is non-empty.

Show possible types

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

### Returns

A [vector store](https://platform.openai.com/docs/api-reference/vector-stores/object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
curl https://api.openai.com/v1/vector_stores \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2"
  -d '{
    "name": "Support FAQ"
  }'
```

```python
1
2
3
4
5
6
7
from openai import OpenAI
client = OpenAI()

vector_store = client.beta.vector_stores.create(
  name="Support FAQ"
)
print(vector_store)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const vectorStore = await openai.beta.vectorStores.create({
    name: "Support FAQ"
  });
  console.log(vectorStore);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
{
  "id": "vs_abc123",
  "object": "vector_store",
  "created_at": 1699061776,
  "name": "Support FAQ",
  "bytes": 139920,
  "file_counts": {
    "in_progress": 0,
    "completed": 3,
    "failed": 0,
    "cancelled": 0,
    "total": 3
  }
}
```

## List vector stores  Beta

gethttps://api.openai.com/v1/vector\_stores

Returns a list of vector stores.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

### Returns

A list of [vector store](https://platform.openai.com/docs/api-reference/vector-stores/object) objects.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/vector_stores \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

vector_stores = client.beta.vector_stores.list()
print(vector_stores)
```

```javascript
1
2
3
4
5
6
7
8
9
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const vectorStores = await openai.beta.vectorStores.list();
  console.log(vectorStores);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
{
  "object": "list",
  "data": [\
    {\
      "id": "vs_abc123",\
      "object": "vector_store",\
      "created_at": 1699061776,\
      "name": "Support FAQ",\
      "bytes": 139920,\
      "file_counts": {\
        "in_progress": 0,\
        "completed": 3,\
        "failed": 0,\
        "cancelled": 0,\
        "total": 3\
      }\
    },\
    {\
      "id": "vs_abc456",\
      "object": "vector_store",\
      "created_at": 1699061776,\
      "name": "Support FAQ v2",\
      "bytes": 139920,\
      "file_counts": {\
        "in_progress": 0,\
        "completed": 3,\
        "failed": 0,\
        "cancelled": 0,\
        "total": 3\
      }\
    }\
  ],
  "first_id": "vs_abc123",
  "last_id": "vs_abc456",
  "has_more": false
}
```

## Retrieve vector store  Beta

gethttps://api.openai.com/v1/vector\_stores/{vector\_store\_id}

Retrieves a vector store.

### Path parameters

vector\_store\_id

string

Required

The ID of the vector store to retrieve.

### Returns

The [vector store](https://platform.openai.com/docs/api-reference/vector-stores/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/vector_stores/vs_abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
6
7
from openai import OpenAI
client = OpenAI()

vector_store = client.beta.vector_stores.retrieve(
  vector_store_id="vs_abc123"
)
print(vector_store)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const vectorStore = await openai.beta.vectorStores.retrieve(
    "vs_abc123"
  );
  console.log(vectorStore);
}

main();
```

Response

```json
1
2
3
4
5
{
  "id": "vs_abc123",
  "object": "vector_store",
  "created_at": 1699061776
}
```

## Modify vector store  Beta

posthttps://api.openai.com/v1/vector\_stores/{vector\_store\_id}

Modifies a vector store.

### Path parameters

vector\_store\_id

string

Required

The ID of the vector store to modify.

### Request body

name

string or null

Optional

The name of the vector store.

expires\_after

object

Optional

The expiration policy for a vector store.

Show properties

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

### Returns

The modified [vector store](https://platform.openai.com/docs/api-reference/vector-stores/object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
curl https://api.openai.com/v1/vector_stores/vs_abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2"
  -d '{
    "name": "Support FAQ"
  }'
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

vector_store = client.beta.vector_stores.update(
  vector_store_id="vs_abc123",
  name="Support FAQ"
)
print(vector_store)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const vectorStore = await openai.beta.vectorStores.update(
    "vs_abc123",
    {
      name: "Support FAQ"
    }
  );
  console.log(vectorStore);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
{
  "id": "vs_abc123",
  "object": "vector_store",
  "created_at": 1699061776,
  "name": "Support FAQ",
  "bytes": 139920,
  "file_counts": {
    "in_progress": 0,
    "completed": 3,
    "failed": 0,
    "cancelled": 0,
    "total": 3
  }
}
```

## Delete vector store  Beta

deletehttps://api.openai.com/v1/vector\_stores/{vector\_store\_id}

Delete a vector store.

### Path parameters

vector\_store\_id

string

Required

The ID of the vector store to delete.

### Returns

Deletion status

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/vector_stores/vs_abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2" \
  -X DELETE
```

```python
1
2
3
4
5
6
7
from openai import OpenAI
client = OpenAI()

deleted_vector_store = client.beta.vector_stores.delete(
  vector_store_id="vs_abc123"
)
print(deleted_vector_store)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const deletedVectorStore = await openai.beta.vectorStores.del(
    "vs_abc123"
  );
  console.log(deletedVectorStore);
}

main();
```

Response

```json
1
2
3
4
5
{
  id: "vs_abc123",
  object: "vector_store.deleted",
  deleted: true
}
```

## The vector store object  Beta

A vector store is a collection of processed files can be used by the `file_search` tool.

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `vector_store`.

created\_at

integer

The Unix timestamp (in seconds) for when the vector store was created.

name

string

The name of the vector store.

usage\_bytes

integer

The total number of bytes used by the files in the vector store.

file\_counts

object

Show properties

status

string

The status of the vector store, which can be either `expired`, `in_progress`, or `completed`. A status of `completed` indicates that the vector store is ready for use.

expires\_after

object

The expiration policy for a vector store.

Show properties

expires\_at

integer or null

The Unix timestamp (in seconds) for when the vector store will expire.

last\_active\_at

integer or null

The Unix timestamp (in seconds) for when the vector store was last active.

metadata

map

Set of 16 key-value pairs that can be attached to an object. This can be
useful for storing additional information about the object in a structured
format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings
with a maximum length of 512 characters.

OBJECT The vector store object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
{
  "id": "vs_123",
  "object": "vector_store",
  "created_at": 1698107661,
  "usage_bytes": 123456,
  "last_active_at": 1698107661,
  "name": "my_vector_store",
  "status": "completed",
  "file_counts": {
    "in_progress": 0,
    "completed": 100,
    "cancelled": 0,
    "failed": 0,
    "total": 100
  },
  "metadata": {},
  "last_used_at": 1698107661
}
```

## Vector store files  Beta

Vector store files represent files inside a vector store.

Related guide: [File Search](https://platform.openai.com/docs/assistants/tools/file-search)

## Create vector store file  Beta

posthttps://api.openai.com/v1/vector\_stores/{vector\_store\_id}/files

Create a vector store file by attaching a [File](https://platform.openai.com/docs/api-reference/files) to a [vector store](https://platform.openai.com/docs/api-reference/vector-stores/object).

### Path parameters

vector\_store\_id

string

Required

The ID of the vector store for which to create a File.

### Request body

file\_id

string

Required

A [File](https://platform.openai.com/docs/api-reference/files) ID that the vector store should use. Useful for tools like `file_search` that can access files.

chunking\_strategy

object

Optional

The chunking strategy used to chunk the file(s). If not set, will use the `auto` strategy.

Show possible types

### Returns

A [vector store file](https://platform.openai.com/docs/api-reference/vector-stores-files/file-object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
curl https://api.openai.com/v1/vector_stores/vs_abc123/files \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -H "OpenAI-Beta: assistants=v2" \
    -d '{
      "file_id": "file-abc123"
    }'
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

vector_store_file = client.beta.vector_stores.files.create(
  vector_store_id="vs_abc123",
  file_id="file-abc123"
)
print(vector_store_file)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const myVectorStoreFile = await openai.beta.vectorStores.files.create(
    "vs_abc123",
    {
      file_id: "file-abc123"
    }
  );
  console.log(myVectorStoreFile);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
{
  "id": "file-abc123",
  "object": "vector_store.file",
  "created_at": 1699061776,
  "usage_bytes": 1234,
  "vector_store_id": "vs_abcd",
  "status": "completed",
  "last_error": null
}
```

## List vector store files  Beta

gethttps://api.openai.com/v1/vector\_stores/{vector\_store\_id}/files

Returns a list of vector store files.

### Path parameters

vector\_store\_id

string

Required

The ID of the vector store that the files belong to.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

filter

string

Optional

Filter by file status. One of `in_progress`, `completed`, `failed`, `cancelled`.

### Returns

A list of [vector store file](https://platform.openai.com/docs/api-reference/vector-stores-files/file-object) objects.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/vector_stores/vs_abc123/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
6
7
from openai import OpenAI
client = OpenAI()

vector_store_files = client.beta.vector_stores.files.list(
  vector_store_id="vs_abc123"
)
print(vector_store_files)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const vectorStoreFiles = await openai.beta.vectorStores.files.list(
    "vs_abc123"
  );
  console.log(vectorStoreFiles);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "object": "list",
  "data": [\
    {\
      "id": "file-abc123",\
      "object": "vector_store.file",\
      "created_at": 1699061776,\
      "vector_store_id": "vs_abc123"\
    },\
    {\
      "id": "file-abc456",\
      "object": "vector_store.file",\
      "created_at": 1699061776,\
      "vector_store_id": "vs_abc123"\
    }\
  ],
  "first_id": "file-abc123",
  "last_id": "file-abc456",
  "has_more": false
}
```

## Retrieve vector store file  Beta

gethttps://api.openai.com/v1/vector\_stores/{vector\_store\_id}/files/{file\_id}

Retrieves a vector store file.

### Path parameters

vector\_store\_id

string

Required

The ID of the vector store that the file belongs to.

file\_id

string

Required

The ID of the file being retrieved.

### Returns

The [vector store file](https://platform.openai.com/docs/api-reference/vector-stores-files/file-object) object.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/vector_stores/vs_abc123/files/file-abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

vector_store_file = client.beta.vector_stores.files.retrieve(
  vector_store_id="vs_abc123",
  file_id="file-abc123"
)
print(vector_store_file)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const vectorStoreFile = await openai.beta.vectorStores.files.retrieve(
    "vs_abc123",
    "file-abc123"
  );
  console.log(vectorStoreFile);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
{
  "id": "file-abc123",
  "object": "vector_store.file",
  "created_at": 1699061776,
  "vector_store_id": "vs_abcd",
  "status": "completed",
  "last_error": null
}
```

## Delete vector store file  Beta

deletehttps://api.openai.com/v1/vector\_stores/{vector\_store\_id}/files/{file\_id}

Delete a vector store file. This will remove the file from the vector store but the file itself will not be deleted. To delete the file, use the [delete file](https://platform.openai.com/docs/api-reference/files/delete) endpoint.

### Path parameters

vector\_store\_id

string

Required

The ID of the vector store that the file belongs to.

file\_id

string

Required

The ID of the file to delete.

### Returns

Deletion status

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/vector_stores/vs_abc123/files/file-abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2" \
  -X DELETE
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

deleted_vector_store_file = client.beta.vector_stores.files.delete(
    vector_store_id="vs_abc123",
    file_id="file-abc123"
)
print(deleted_vector_store_file)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const deletedVectorStoreFile = await openai.beta.vectorStores.files.del(
    "vs_abc123",
    "file-abc123"
  );
  console.log(deletedVectorStoreFile);
}

main();
```

Response

```json
1
2
3
4
5
{
  id: "file-abc123",
  object: "vector_store.file.deleted",
  deleted: true
}
```

## The vector store file object  Beta

A list of files attached to a vector store.

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `vector_store.file`.

usage\_bytes

integer

The total vector store usage in bytes. Note that this may be different from the original file size.

created\_at

integer

The Unix timestamp (in seconds) for when the vector store file was created.

vector\_store\_id

string

The ID of the [vector store](https://platform.openai.com/docs/api-reference/vector-stores/object) that the [File](https://platform.openai.com/docs/api-reference/files) is attached to.

status

string

The status of the vector store file, which can be either `in_progress`, `completed`, `cancelled`, or `failed`. The status `completed` indicates that the vector store file is ready for use.

last\_error

object or null

The last error associated with this vector store file. Will be `null` if there are no errors.

Show properties

chunking\_strategy

object

The strategy used to chunk the file.

Show possible types

OBJECT The vector store file object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
{
  "id": "file-abc123",
  "object": "vector_store.file",
  "usage_bytes": 1234,
  "created_at": 1698107661,
  "vector_store_id": "vs_abc123",
  "status": "completed",
  "last_error": null,
  "chunking_strategy": {
    "type": "static",
    "static": {
      "max_chunk_size_tokens": 800,
      "chunk_overlap_tokens": 400
    }
  }
}
```

## Vector store file batches  Beta

Vector store file batches represent operations to add multiple files to a vector store.
Related guide: [File Search](https://platform.openai.com/docs/assistants/tools/file-search)

## Create vector store file batch  Beta

posthttps://api.openai.com/v1/vector\_stores/{vector\_store\_id}/file\_batches

Create a vector store file batch.

### Path parameters

vector\_store\_id

string

Required

The ID of the vector store for which to create a File Batch.

### Request body

file\_ids

array

Required

A list of [File](https://platform.openai.com/docs/api-reference/files) IDs that the vector store should use. Useful for tools like `file_search` that can access files.

chunking\_strategy

object

Optional

The chunking strategy used to chunk the file(s). If not set, will use the `auto` strategy.

Show possible types

### Returns

A [vector store file batch](https://platform.openai.com/docs/api-reference/vector-stores-file-batches/batch-object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
curl https://api.openai.com/v1/vector_stores/vs_abc123/file_batches \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json \
    -H "OpenAI-Beta: assistants=v2" \
    -d '{
      "file_ids": ["file-abc123", "file-abc456"]
    }'
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

vector_store_file_batch = client.beta.vector_stores.file_batches.create(
  vector_store_id="vs_abc123",
  file_ids=["file-abc123", "file-abc456"]
)
print(vector_store_file_batch)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const myVectorStoreFileBatch = await openai.beta.vectorStores.fileBatches.create(
    "vs_abc123",
    {
      file_ids: ["file-abc123", "file-abc456"]
    }
  );
  console.log(myVectorStoreFileBatch);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
{
  "id": "vsfb_abc123",
  "object": "vector_store.file_batch",
  "created_at": 1699061776,
  "vector_store_id": "vs_abc123",
  "status": "in_progress",
  "file_counts": {
    "in_progress": 1,
    "completed": 1,
    "failed": 0,
    "cancelled": 0,
    "total": 0,
  }
}
```

## Retrieve vector store file batch  Beta

gethttps://api.openai.com/v1/vector\_stores/{vector\_store\_id}/file\_batches/{batch\_id}

Retrieves a vector store file batch.

### Path parameters

vector\_store\_id

string

Required

The ID of the vector store that the file batch belongs to.

batch\_id

string

Required

The ID of the file batch being retrieved.

### Returns

The [vector store file batch](https://platform.openai.com/docs/api-reference/vector-stores-file-batches/batch-object) object.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/vector_stores/vs_abc123/files_batches/vsfb_abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

vector_store_file_batch = client.beta.vector_stores.file_batches.retrieve(
  vector_store_id="vs_abc123",
  batch_id="vsfb_abc123"
)
print(vector_store_file_batch)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const vectorStoreFileBatch = await openai.beta.vectorStores.fileBatches.retrieve(
    "vs_abc123",
    "vsfb_abc123"
  );
  console.log(vectorStoreFileBatch);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
{
  "id": "vsfb_abc123",
  "object": "vector_store.file_batch",
  "created_at": 1699061776,
  "vector_store_id": "vs_abc123",
  "status": "in_progress",
  "file_counts": {
    "in_progress": 1,
    "completed": 1,
    "failed": 0,
    "cancelled": 0,
    "total": 0,
  }
}
```

## Cancel vector store file batch  Beta

posthttps://api.openai.com/v1/vector\_stores/{vector\_store\_id}/file\_batches/{batch\_id}/cancel

Cancel a vector store file batch. This attempts to cancel the processing of files in this batch as soon as possible.

### Path parameters

vector\_store\_id

string

Required

The ID of the vector store that the file batch belongs to.

batch\_id

string

Required

The ID of the file batch to cancel.

### Returns

The modified vector store file batch object.

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/vector_stores/vs_abc123/files_batches/vsfb_abc123/cancel \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2" \
  -X POST
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

deleted_vector_store_file_batch = client.beta.vector_stores.file_batches.cancel(
    vector_store_id="vs_abc123",
    file_batch_id="vsfb_abc123"
)
print(deleted_vector_store_file_batch)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const deletedVectorStoreFileBatch = await openai.vector_stores.fileBatches.cancel(
    "vs_abc123",
    "vsfb_abc123"
  );
  console.log(deletedVectorStoreFileBatch);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
{
  "id": "vsfb_abc123",
  "object": "vector_store.file_batch",
  "created_at": 1699061776,
  "vector_store_id": "vs_abc123",
  "status": "in_progress",
  "file_counts": {
    "in_progress": 12,
    "completed": 3,
    "failed": 0,
    "cancelled": 0,
    "total": 15,
  }
}
```

## List vector store files in a batch  Beta

gethttps://api.openai.com/v1/vector\_stores/{vector\_store\_id}/file\_batches/{batch\_id}/files

Returns a list of vector store files in a batch.

### Path parameters

vector\_store\_id

string

Required

The ID of the vector store that the files belong to.

batch\_id

string

Required

The ID of the file batch that the files belong to.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

filter

string

Optional

Filter by file status. One of `in_progress`, `completed`, `failed`, `cancelled`.

### Returns

A list of [vector store file](https://platform.openai.com/docs/api-reference/vector-stores-files/file-object) objects.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/vector_stores/vs_abc123/files_batches/vsfb_abc123/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

vector_store_files = client.beta.vector_stores.file_batches.list_files(
  vector_store_id="vs_abc123",
  batch_id="vsfb_abc123"
)
print(vector_store_files)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const vectorStoreFiles = await openai.beta.vectorStores.fileBatches.listFiles(
    "vs_abc123",
    "vsfb_abc123"
  );
  console.log(vectorStoreFiles);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "object": "list",
  "data": [\
    {\
      "id": "file-abc123",\
      "object": "vector_store.file",\
      "created_at": 1699061776,\
      "vector_store_id": "vs_abc123"\
    },\
    {\
      "id": "file-abc456",\
      "object": "vector_store.file",\
      "created_at": 1699061776,\
      "vector_store_id": "vs_abc123"\
    }\
  ],
  "first_id": "file-abc123",
  "last_id": "file-abc456",
  "has_more": false
}
```

## The vector store files batch object  Beta

A batch of files attached to a vector store.

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `vector_store.file_batch`.

created\_at

integer

The Unix timestamp (in seconds) for when the vector store files batch was created.

vector\_store\_id

string

The ID of the [vector store](https://platform.openai.com/docs/api-reference/vector-stores/object) that the [File](https://platform.openai.com/docs/api-reference/files) is attached to.

status

string

The status of the vector store files batch, which can be either `in_progress`, `completed`, `cancelled` or `failed`.

file\_counts

object

Show properties

OBJECT The vector store files batch object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
{
  "id": "vsfb_123",
  "object": "vector_store.files_batch",
  "created_at": 1698107661,
  "vector_store_id": "vs_abc123",
  "status": "completed",
  "file_counts": {
    "in_progress": 0,
    "completed": 100,
    "failed": 0,
    "cancelled": 0,
    "total": 100
  }
}
```

## Streaming  Beta

Stream the result of executing a Run or resuming a Run after submitting tool outputs.
You can stream events from the [Create Thread and Run](https://platform.openai.com/docs/api-reference/runs/createThreadAndRun),
[Create Run](https://platform.openai.com/docs/api-reference/runs/createRun), and [Submit Tool Outputs](https://platform.openai.com/docs/api-reference/runs/submitToolOutputs)
endpoints by passing `"stream": true`. The response will be a [Server-Sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events) stream.
Our Node and Python SDKs provide helpful utilities to make streaming easy. Reference the
[Assistants API quickstart](https://platform.openai.com/docs/assistants/overview) to learn more.

## The message delta object  Beta

Represents a message delta i.e. any changed fields on a message during streaming.

id

string

The identifier of the message, which can be referenced in API endpoints.

object

string

The object type, which is always `thread.message.delta`.

delta

object

The delta containing the fields that have changed on the Message.

Show properties

OBJECT The message delta object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
{
  "id": "msg_123",
  "object": "thread.message.delta",
  "delta": {
    "content": [\
      {\
        "index": 0,\
        "type": "text",\
        "text": { "value": "Hello", "annotations": [] }\
      }\
    ]
  }
}
```

## The run step delta object  Beta

Represents a run step delta i.e. any changed fields on a run step during streaming.

id

string

The identifier of the run step, which can be referenced in API endpoints.

object

string

The object type, which is always `thread.run.step.delta`.

delta

object

The delta containing the fields that have changed on the run step.

Show properties

OBJECT The run step delta object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
{
  "id": "step_123",
  "object": "thread.run.step.delta",
  "delta": {
    "step_details": {
      "type": "tool_calls",
      "tool_calls": [\
        {\
          "index": 0,\
          "id": "call_123",\
          "type": "code_interpreter",\
          "code_interpreter": { "input": "", "outputs": [] }\
        }\
      ]
    }
  }
}
```

## Assistant stream events  Beta

Represents an event emitted when streaming a Run.

Each event in a server-sent events stream has an `event` and `data` property:

```text
event: thread.created
data: {"id": "thread_123", "object": "thread", ...}
```

We emit events whenever a new object is created, transitions to a new state, or is being
streamed in parts (deltas). For example, we emit `thread.run.created` when a new run
is created, `thread.run.completed` when a run completes, and so on. When an Assistant chooses
to create a message during a run, we emit a `thread.message.created event`, a
`thread.message.in_progress` event, many `thread.message.delta` events, and finally a
`thread.message.completed` event.

We may add additional events over time, so we recommend handling unknown events gracefully
in your code. See the [Assistants API quickstart](https://platform.openai.com/docs/assistants/overview) to learn how to
integrate the Assistants API with streaming.

thread.created

`data` is a [thread](https://platform.openai.com/docs/api-reference/threads/object)

Occurs when a new [thread](https://platform.openai.com/docs/api-reference/threads/object) is created.

thread.run.created

`data` is a [run](https://platform.openai.com/docs/api-reference/runs/object)

Occurs when a new [run](https://platform.openai.com/docs/api-reference/runs/object) is created.

thread.run.queued

`data` is a [run](https://platform.openai.com/docs/api-reference/runs/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs/object) moves to a `queued` status.

thread.run.in\_progress

`data` is a [run](https://platform.openai.com/docs/api-reference/runs/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs/object) moves to an `in_progress` status.

thread.run.requires\_action

`data` is a [run](https://platform.openai.com/docs/api-reference/runs/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs/object) moves to a `requires_action` status.

thread.run.completed

`data` is a [run](https://platform.openai.com/docs/api-reference/runs/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs/object) is completed.

thread.run.incomplete

`data` is a [run](https://platform.openai.com/docs/api-reference/runs/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs/object) ends with status `incomplete`.

thread.run.failed

`data` is a [run](https://platform.openai.com/docs/api-reference/runs/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs/object) fails.

thread.run.cancelling

`data` is a [run](https://platform.openai.com/docs/api-reference/runs/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs/object) moves to a `cancelling` status.

thread.run.cancelled

`data` is a [run](https://platform.openai.com/docs/api-reference/runs/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs/object) is cancelled.

thread.run.expired

`data` is a [run](https://platform.openai.com/docs/api-reference/runs/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs/object) expires.

thread.run.step.created

`data` is a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object)

Occurs when a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object) is created.

thread.run.step.in\_progress

`data` is a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object)

Occurs when a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object) moves to an `in_progress` state.

thread.run.step.delta

`data` is a [run step delta](https://platform.openai.com/docs/api-reference/assistants-streaming/run-step-delta-object)

Occurs when parts of a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object) are being streamed.

thread.run.step.completed

`data` is a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object)

Occurs when a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object) is completed.

thread.run.step.failed

`data` is a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object)

Occurs when a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object) fails.

thread.run.step.cancelled

`data` is a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object)

Occurs when a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object) is cancelled.

thread.run.step.expired

`data` is a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object)

Occurs when a [run step](https://platform.openai.com/docs/api-reference/run-steps/step-object) expires.

thread.message.created

`data` is a [message](https://platform.openai.com/docs/api-reference/messages/object)

Occurs when a [message](https://platform.openai.com/docs/api-reference/messages/object) is created.

thread.message.in\_progress

`data` is a [message](https://platform.openai.com/docs/api-reference/messages/object)

Occurs when a [message](https://platform.openai.com/docs/api-reference/messages/object) moves to an `in_progress` state.

thread.message.delta

`data` is a [message delta](https://platform.openai.com/docs/api-reference/assistants-streaming/message-delta-object)

Occurs when parts of a [Message](https://platform.openai.com/docs/api-reference/messages/object) are being streamed.

thread.message.completed

`data` is a [message](https://platform.openai.com/docs/api-reference/messages/object)

Occurs when a [message](https://platform.openai.com/docs/api-reference/messages/object) is completed.

thread.message.incomplete

`data` is a [message](https://platform.openai.com/docs/api-reference/messages/object)

Occurs when a [message](https://platform.openai.com/docs/api-reference/messages/object) ends before it is completed.

error

`data` is an [error](https://platform.openai.com/docs/guides/error-codes#api-errors)

Occurs when an [error](https://platform.openai.com/docs/guides/error-codes#api-errors) occurs. This can happen due to an internal server error or a timeout.

done

`data` is `[DONE]`

Occurs when a stream ends.

## Administration

Programmatically manage your organization.
The Audit Logs endpoint provides a log of all actions taken in the organization for security and monitoring purposes.
To access these endpoints please generate an Admin API Key through the [API Platform Organization overview](https://platform.openai.com/organization/admin-keys). Admin API keys cannot be used for non-administration endpoints.
For best practices on setting up your organization, please refer to this [guide](https://platform.openai.com/docs/guides/production-best-practices#setting-up-your-organization)

## Admin API Keys

The **Usage API** provides detailed insights into your activity across the OpenAI API. It also includes a separate [Costs endpoint](https://platform.openai.com/docs/api-reference/usage/costs), which offers visibility into your spend, breaking down consumption by invoice line items and project IDs.
While the Usage API delivers granular usage data, it may not always reconcile perfectly with the Costs due to minor differences in how usage and spend are recorded. For financial purposes, we recommend using the [Costs endpoint](https://platform.openai.com/docs/api-reference/usage/costs) or the [Costs tab](https://platform.openai.com/settings/organization/usage) in the Usage Dashboard, which will reconcile back to your billing invoice.

## List admin API keys

gethttps://api.openai.com/v1/organization/admin\_api\_keys

List organization API keys

### Query parameters

after

string or null

Optional

order

string

Optional

Defaults to asc

limit

integer

Optional

Defaults to 20

### Returns

A list of admin API key objects.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/admin_api_keys?after=key_abc&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
{
  "object": "list",
  "data": [\
    {\
      "object": "organization.admin_api_key",\
      "id": "key_abc",\
      "name": "Main Admin Key",\
      "redacted_value": "sk-admin...def",\
      "created_at": 1711471533,\
      "owner": {\
        "type": "service_account",\
        "object": "organization.service_account",\
        "id": "sa_456",\
        "name": "My Service Account",\
        "created_at": 1711471533,\
        "role": "member"\
      }\
    }\
  ],
  "first_id": "key_abc",
  "last_id": "key_abc",
  "has_more": false
}
```

## Create admin API key

posthttps://api.openai.com/v1/organization/admin\_api\_keys

Create an organization admin API key

### Request body

name

string

Required

### Returns

The created admin API key object.

Example request

curl

```bash
1
2
3
4
5
6
curl -X POST https://api.openai.com/v1/organization/admin_api_keys \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "name": "New Admin Key"
  }'
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
{
  "object": "organization.admin_api_key",
  "id": "key_xyz",
  "name": "New Admin Key",
  "redacted_value": "sk-admin...xyz",
  "created_at": 1711471533,
  "owner": {
    "type": "user",
    "object": "organization.user",
    "id": "user_123",
    "name": "John Doe",
    "created_at": 1711471533,
    "role": "owner"
  },
  "value": "sk-admin-1234abcd"
}
```

## Retrieve admin API key

gethttps://api.openai.com/v1/organization/admin\_api\_keys/{key\_id}

Retrieve a single organization API key

### Path parameters

key\_id

string

Required

### Returns

The requested admin API key object.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/admin_api_keys/key_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
{
  "object": "organization.admin_api_key",
  "id": "key_abc",
  "name": "Main Admin Key",
  "redacted_value": "sk-admin...xyz",
  "created_at": 1711471533,
  "owner": {
    "type": "user",
    "object": "organization.user",
    "id": "user_123",
    "name": "John Doe",
    "created_at": 1711471533,
    "role": "owner"
  }
}
```

## Delete admin API key

deletehttps://api.openai.com/v1/organization/admin\_api\_keys/{key\_id}

Delete an organization admin API key

### Path parameters

key\_id

string

Required

### Returns

A confirmation object indicating the key was deleted.

Example request

curl

```bash
1
2
3
curl -X DELETE https://api.openai.com/v1/organization/admin_api_keys/key_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
{
  "id": "key_abc",
  "object": "organization.admin_api_key.deleted",
  "deleted": true
}
```

## Invites

Invite and manage invitations for an organization.

## List invites

gethttps://api.openai.com/v1/organization/invites

Returns a list of invites in the organization.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

### Returns

A list of [Invite](https://platform.openai.com/docs/api-reference/invite/object) objects.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/invites?after=invite-abc&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
{
  "object": "list",
  "data": [\
    {\
      "object": "organization.invite",\
      "id": "invite-abc",\
      "email": "user@example.com",\
      "role": "owner",\
      "status": "accepted",\
      "invited_at": 1711471533,\
      "expires_at": 1711471533,\
      "accepted_at": 1711471533\
    }\
  ],
  "first_id": "invite-abc",
  "last_id": "invite-abc",
  "has_more": false
}
```

## Create invite

posthttps://api.openai.com/v1/organization/invites

Create an invite for a user to the organization. The invite must be accepted by the user before they have access to the organization.

### Request body

email

string

Required

Send an email to this address

role

string

Required

`owner` or `reader`

projects

array

Optional

An array of projects to which membership is granted at the same time the org invite is accepted. If omitted, the user will be invited to the default project for compatibility with legacy behavior.

Show properties

### Returns

The created [Invite](https://platform.openai.com/docs/api-reference/invite/object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
curl -X POST https://api.openai.com/v1/organization/invites \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "email": "anotheruser@example.com",
      "role": "reader",
      "projects": [\
        {\
          "id": "project-xyz",\
          "role": "member"\
        },\
        {\
          "id": "project-abc",\
          "role": "owner"\
        }\
      ]
  }'
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "object": "organization.invite",
  "id": "invite-def",
  "email": "anotheruser@example.com",
  "role": "reader",
  "status": "pending",
  "invited_at": 1711471533,
  "expires_at": 1711471533,
  "accepted_at": null,
  "projects": [\
    {\
      "id": "project-xyz",\
      "role": "member"\
    },\
    {\
      "id": "project-abc",\
      "role": "owner"\
    }\
  ]
}
```

## Retrieve invite

gethttps://api.openai.com/v1/organization/invites/{invite\_id}

Retrieves an invite.

### Path parameters

invite\_id

string

Required

The ID of the invite to retrieve.

### Returns

The [Invite](https://platform.openai.com/docs/api-reference/invite/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/invites/invite-abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
{
    "object": "organization.invite",
    "id": "invite-abc",
    "email": "user@example.com",
    "role": "owner",
    "status": "accepted",
    "invited_at": 1711471533,
    "expires_at": 1711471533,
    "accepted_at": 1711471533
}
```

## Delete invite

deletehttps://api.openai.com/v1/organization/invites/{invite\_id}

Delete an invite. If the invite has already been accepted, it cannot be deleted.

### Path parameters

invite\_id

string

Required

The ID of the invite to delete.

### Returns

Confirmation that the invite has been deleted

Example request

curl

```bash
1
2
3
curl -X DELETE https://api.openai.com/v1/organization/invites/invite-abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
{
    "object": "organization.invite.deleted",
    "id": "invite-abc",
    "deleted": true
}
```

## The invite object

Represents an individual `invite` to the organization.

object

string

The object type, which is always `organization.invite`

id

string

The identifier, which can be referenced in API endpoints

email

string

The email address of the individual to whom the invite was sent

role

string

`owner` or `reader`

status

string

`accepted`, `expired`, or `pending`

invited\_at

integer

The Unix timestamp (in seconds) of when the invite was sent.

expires\_at

integer

The Unix timestamp (in seconds) of when the invite expires.

accepted\_at

integer

The Unix timestamp (in seconds) of when the invite was accepted.

projects

array

The projects that were granted membership upon acceptance of the invite.

Show properties

OBJECT The invite object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
{
  "object": "organization.invite",
  "id": "invite-abc",
  "email": "user@example.com",
  "role": "owner",
  "status": "accepted",
  "invited_at": 1711471533,
  "expires_at": 1711471533,
  "accepted_at": 1711471533,
  "projects": [\
    {\
      "id": "project-xyz",\
      "role": "member"\
    }\
  ]
}
```

## Users

Manage users and their role in an organization.

## List users

gethttps://api.openai.com/v1/organization/users

Lists all of the users in the organization.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

emails

array

Optional

Filter by the email address of users.

### Returns

A list of [User](https://platform.openai.com/docs/api-reference/users/object) objects.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/users?after=user_abc&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
{
    "object": "list",
    "data": [\
        {\
            "object": "organization.user",\
            "id": "user_abc",\
            "name": "First Last",\
            "email": "user@example.com",\
            "role": "owner",\
            "added_at": 1711471533\
        }\
    ],
    "first_id": "user-abc",
    "last_id": "user-xyz",
    "has_more": false
}
```

## Modify user

posthttps://api.openai.com/v1/organization/users/{user\_id}

Modifies a user's role in the organization.

### Path parameters

user\_id

string

Required

The ID of the user.

### Request body

role

string

Required

`owner` or `reader`

### Returns

The updated [User](https://platform.openai.com/docs/api-reference/users/object) object.

Example request

curl

```bash
1
2
3
4
5
6
curl -X POST https://api.openai.com/v1/organization/users/user_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "role": "owner"
  }'
```

Response

```json
1
2
3
4
5
6
7
8
{
    "object": "organization.user",
    "id": "user_abc",
    "name": "First Last",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
```

## Retrieve user

gethttps://api.openai.com/v1/organization/users/{user\_id}

Retrieves a user by their identifier.

### Path parameters

user\_id

string

Required

The ID of the user.

### Returns

The [User](https://platform.openai.com/docs/api-reference/users/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/users/user_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
{
    "object": "organization.user",
    "id": "user_abc",
    "name": "First Last",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
```

## Delete user

deletehttps://api.openai.com/v1/organization/users/{user\_id}

Deletes a user from the organization.

### Path parameters

user\_id

string

Required

The ID of the user.

### Returns

Confirmation of the deleted user

Example request

curl

```bash
1
2
3
curl -X DELETE https://api.openai.com/v1/organization/users/user_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
{
    "object": "organization.user.deleted",
    "id": "user_abc",
    "deleted": true
}
```

## The user object

Represents an individual `user` within an organization.

object

string

The object type, which is always `organization.user`

id

string

The identifier, which can be referenced in API endpoints

name

string

The name of the user

email

string

The email address of the user

role

string

`owner` or `reader`

added\_at

integer

The Unix timestamp (in seconds) of when the user was added.

OBJECT The user object

```JSON
1
2
3
4
5
6
7
8
{
    "object": "organization.user",
    "id": "user_abc",
    "name": "First Last",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
```

## Projects

Manage the projects within an orgnanization includes creation, updating, and archiving or projects.
The Default project cannot be archived.

## List projects

gethttps://api.openai.com/v1/organization/projects

Returns a list of projects.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

include\_archived

boolean

Optional

Defaults to false

If `true` returns all projects including those that have been `archived`. Archived projects are not included by default.

### Returns

A list of [Project](https://platform.openai.com/docs/api-reference/projects/object) objects.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/projects?after=proj_abc&limit=20&include_archived=false \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
{
    "object": "list",
    "data": [\
        {\
            "id": "proj_abc",\
            "object": "organization.project",\
            "name": "Project example",\
            "created_at": 1711471533,\
            "archived_at": null,\
            "status": "active"\
        }\
    ],
    "first_id": "proj-abc",
    "last_id": "proj-xyz",
    "has_more": false
}
```

## Create project

posthttps://api.openai.com/v1/organization/projects

Create a new project in the organization. Projects can be created and archived, but cannot be deleted.

### Request body

name

string

Required

The friendly name of the project, this name appears in reports.

### Returns

The created [Project](https://platform.openai.com/docs/api-reference/projects/object) object.

Example request

curl

```bash
1
2
3
4
5
6
curl -X POST https://api.openai.com/v1/organization/projects \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "name": "Project ABC"
  }'
```

Response

```json
1
2
3
4
5
6
7
8
{
    "id": "proj_abc",
    "object": "organization.project",
    "name": "Project ABC",
    "created_at": 1711471533,
    "archived_at": null,
    "status": "active"
}
```

## Retrieve project

gethttps://api.openai.com/v1/organization/projects/{project\_id}

Retrieves a project.

### Path parameters

project\_id

string

Required

The ID of the project.

### Returns

The [Project](https://platform.openai.com/docs/api-reference/projects/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/projects/proj_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
{
    "id": "proj_abc",
    "object": "organization.project",
    "name": "Project example",
    "created_at": 1711471533,
    "archived_at": null,
    "status": "active"
}
```

## Modify project

posthttps://api.openai.com/v1/organization/projects/{project\_id}

Modifies a project in the organization.

### Path parameters

project\_id

string

Required

The ID of the project.

### Request body

name

string

Required

The updated name of the project, this name appears in reports.

### Returns

The updated [Project](https://platform.openai.com/docs/api-reference/projects/object) object.

Example request

curl

```bash
1
2
3
4
5
6
curl -X POST https://api.openai.com/v1/organization/projects/proj_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "name": "Project DEF"
  }'
```

## Archive project

posthttps://api.openai.com/v1/organization/projects/{project\_id}/archive

Archives a project in the organization. Archived projects cannot be used or updated.

### Path parameters

project\_id

string

Required

The ID of the project.

### Returns

The archived [Project](https://platform.openai.com/docs/api-reference/projects/object) object.

Example request

curl

```bash
1
2
3
curl -X POST https://api.openai.com/v1/organization/projects/proj_abc/archive \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
{
    "id": "proj_abc",
    "object": "organization.project",
    "name": "Project DEF",
    "created_at": 1711471533,
    "archived_at": 1711471533,
    "status": "archived"
}
```

## The project object

Represents an individual project.

id

string

The identifier, which can be referenced in API endpoints

object

string

The object type, which is always `organization.project`

name

string

The name of the project. This appears in reporting.

created\_at

integer

The Unix timestamp (in seconds) of when the project was created.

archived\_at

integer or null

The Unix timestamp (in seconds) of when the project was archived or `null`.

status

string

`active` or `archived`

OBJECT The project object

```JSON
1
2
3
4
5
6
7
8
{
    "id": "proj_abc",
    "object": "organization.project",
    "name": "Project example",
    "created_at": 1711471533,
    "archived_at": null,
    "status": "active"
}
```

## Project users

Manage users within a project, including adding, updating roles, and removing users.

## List project users

gethttps://api.openai.com/v1/organization/projects/{project\_id}/users

Returns a list of users in the project.

### Path parameters

project\_id

string

Required

The ID of the project.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

### Returns

A list of [ProjectUser](https://platform.openai.com/docs/api-reference/project-users/object) objects.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/projects/proj_abc/users?after=user_abc&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
{
    "object": "list",
    "data": [\
        {\
            "object": "organization.project.user",\
            "id": "user_abc",\
            "name": "First Last",\
            "email": "user@example.com",\
            "role": "owner",\
            "added_at": 1711471533\
        }\
    ],
    "first_id": "user-abc",
    "last_id": "user-xyz",
    "has_more": false
}
```

## Create project user

posthttps://api.openai.com/v1/organization/projects/{project\_id}/users

Adds a user to the project. Users must already be members of the organization to be added to a project.

### Path parameters

project\_id

string

Required

The ID of the project.

### Request body

user\_id

string

Required

The ID of the user.

role

string

Required

`owner` or `member`

### Returns

The created [ProjectUser](https://platform.openai.com/docs/api-reference/project-users/object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
curl -X POST https://api.openai.com/v1/organization/projects/proj_abc/users \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "user_id": "user_abc",
      "role": "member"
  }'
```

Response

```json
1
2
3
4
5
6
7
{
    "object": "organization.project.user",
    "id": "user_abc",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
```

## Retrieve project user

gethttps://api.openai.com/v1/organization/projects/{project\_id}/users/{user\_id}

Retrieves a user in the project.

### Path parameters

project\_id

string

Required

The ID of the project.

user\_id

string

Required

The ID of the user.

### Returns

The [ProjectUser](https://platform.openai.com/docs/api-reference/project-users/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/projects/proj_abc/users/user_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
{
    "object": "organization.project.user",
    "id": "user_abc",
    "name": "First Last",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
```

## Modify project user

posthttps://api.openai.com/v1/organization/projects/{project\_id}/users/{user\_id}

Modifies a user's role in the project.

### Path parameters

project\_id

string

Required

The ID of the project.

user\_id

string

Required

The ID of the user.

### Request body

role

string

Required

`owner` or `member`

### Returns

The updated [ProjectUser](https://platform.openai.com/docs/api-reference/project-users/object) object.

Example request

curl

```bash
1
2
3
4
5
6
curl -X POST https://api.openai.com/v1/organization/projects/proj_abc/users/user_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "role": "owner"
  }'
```

Response

```json
1
2
3
4
5
6
7
8
{
    "object": "organization.project.user",
    "id": "user_abc",
    "name": "First Last",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
```

## Delete project user

deletehttps://api.openai.com/v1/organization/projects/{project\_id}/users/{user\_id}

Deletes a user from the project.

### Path parameters

project\_id

string

Required

The ID of the project.

user\_id

string

Required

The ID of the user.

### Returns

Confirmation that project has been deleted or an error in case of an archived project, which has no users

Example request

curl

```bash
1
2
3
curl -X DELETE https://api.openai.com/v1/organization/projects/proj_abc/users/user_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
{
    "object": "organization.project.user.deleted",
    "id": "user_abc",
    "deleted": true
}
```

## The project user object

Represents an individual user in a project.

object

string

The object type, which is always `organization.project.user`

id

string

The identifier, which can be referenced in API endpoints

name

string

The name of the user

email

string

The email address of the user

role

string

`owner` or `member`

added\_at

integer

The Unix timestamp (in seconds) of when the project was added.

OBJECT The project user object

```JSON
1
2
3
4
5
6
7
8
{
    "object": "organization.project.user",
    "id": "user_abc",
    "name": "First Last",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
```

## Project service accounts

Manage service accounts within a project. A service account is a bot user that is not associated with a user.
If a user leaves an organization, their keys and membership in projects will no longer work. Service accounts
do not have this limitation. However, service accounts can also be deleted from a project.

## List project service accounts

gethttps://api.openai.com/v1/organization/projects/{project\_id}/service\_accounts

Returns a list of service accounts in the project.

### Path parameters

project\_id

string

Required

The ID of the project.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

### Returns

A list of [ProjectServiceAccount](https://platform.openai.com/docs/api-reference/project-service-accounts/object) objects.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/projects/proj_abc/service_accounts?after=custom_id&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
{
    "object": "list",
    "data": [\
        {\
            "object": "organization.project.service_account",\
            "id": "svc_acct_abc",\
            "name": "Service Account",\
            "role": "owner",\
            "created_at": 1711471533\
        }\
    ],
    "first_id": "svc_acct_abc",
    "last_id": "svc_acct_xyz",
    "has_more": false
}
```

## Create project service account

posthttps://api.openai.com/v1/organization/projects/{project\_id}/service\_accounts

Creates a new service account in the project. This also returns an unredacted API key for the service account.

### Path parameters

project\_id

string

Required

The ID of the project.

### Request body

name

string

Required

The name of the service account being created.

### Returns

The created [ProjectServiceAccount](https://platform.openai.com/docs/api-reference/project-service-accounts/object) object.

Example request

curl

```bash
1
2
3
4
5
6
curl -X POST https://api.openai.com/v1/organization/projects/proj_abc/service_accounts \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "name": "Production App"
  }'
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
{
    "object": "organization.project.service_account",
    "id": "svc_acct_abc",
    "name": "Production App",
    "role": "member",
    "created_at": 1711471533,
    "api_key": {
        "object": "organization.project.service_account.api_key",
        "value": "sk-abcdefghijklmnop123",
        "name": "Secret Key",
        "created_at": 1711471533,
        "id": "key_abc"
    }
}
```

## Retrieve project service account

gethttps://api.openai.com/v1/organization/projects/{project\_id}/service\_accounts/{service\_account\_id}

Retrieves a service account in the project.

### Path parameters

project\_id

string

Required

The ID of the project.

service\_account\_id

string

Required

The ID of the service account.

### Returns

The [ProjectServiceAccount](https://platform.openai.com/docs/api-reference/project-service-accounts/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/projects/proj_abc/service_accounts/svc_acct_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
{
    "object": "organization.project.service_account",
    "id": "svc_acct_abc",
    "name": "Service Account",
    "role": "owner",
    "created_at": 1711471533
}
```

## Delete project service account

deletehttps://api.openai.com/v1/organization/projects/{project\_id}/service\_accounts/{service\_account\_id}

Deletes a service account from the project.

### Path parameters

project\_id

string

Required

The ID of the project.

service\_account\_id

string

Required

The ID of the service account.

### Returns

Confirmation of service account being deleted, or an error in case of an archived project, which has no service accounts

Example request

curl

```bash
1
2
3
curl -X DELETE https://api.openai.com/v1/organization/projects/proj_abc/service_accounts/svc_acct_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
{
    "object": "organization.project.service_account.deleted",
    "id": "svc_acct_abc",
    "deleted": true
}
```

## The project service account object

Represents an individual service account in a project.

object

string

The object type, which is always `organization.project.service_account`

id

string

The identifier, which can be referenced in API endpoints

name

string

The name of the service account

role

string

`owner` or `member`

created\_at

integer

The Unix timestamp (in seconds) of when the service account was created

OBJECT The project service account object

```JSON
1
2
3
4
5
6
7
{
    "object": "organization.project.service_account",
    "id": "svc_acct_abc",
    "name": "Service Account",
    "role": "owner",
    "created_at": 1711471533
}
```

## Project API keys

Manage API keys for a given project. Supports listing and deleting keys for users.
This API does not allow issuing keys for users, as users need to authorize themselves to generate keys.

## List project API keys

gethttps://api.openai.com/v1/organization/projects/{project\_id}/api\_keys

Returns a list of API keys in the project.

### Path parameters

project\_id

string

Required

The ID of the project.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

### Returns

A list of [ProjectApiKey](https://platform.openai.com/docs/api-reference/project-api-keys/object) objects.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/projects/proj_abc/api_keys?after=key_abc&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
{
    "object": "list",
    "data": [\
        {\
            "object": "organization.project.api_key",\
            "redacted_value": "sk-abc...def",\
            "name": "My API Key",\
            "created_at": 1711471533,\
            "id": "key_abc",\
            "owner": {\
                "type": "user",\
                "user": {\
                    "object": "organization.project.user",\
                    "id": "user_abc",\
                    "name": "First Last",\
                    "email": "user@example.com",\
                    "role": "owner",\
                    "added_at": 1711471533\
                }\
            }\
        }\
    ],
    "first_id": "key_abc",
    "last_id": "key_xyz",
    "has_more": false
}
```

## Retrieve project API key

gethttps://api.openai.com/v1/organization/projects/{project\_id}/api\_keys/{key\_id}

Retrieves an API key in the project.

### Path parameters

project\_id

string

Required

The ID of the project.

key\_id

string

Required

The ID of the API key.

### Returns

The [ProjectApiKey](https://platform.openai.com/docs/api-reference/project-api-keys/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/projects/proj_abc/api_keys/key_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
{
    "object": "organization.project.api_key",
    "redacted_value": "sk-abc...def",
    "name": "My API Key",
    "created_at": 1711471533,
    "id": "key_abc",
    "owner": {
        "type": "user",
        "user": {
            "object": "organization.project.user",
            "id": "user_abc",
            "name": "First Last",
            "email": "user@example.com",
            "role": "owner",
            "added_at": 1711471533
        }
    }
}
```

## Delete project API key

deletehttps://api.openai.com/v1/organization/projects/{project\_id}/api\_keys/{key\_id}

Deletes an API key from the project.

### Path parameters

project\_id

string

Required

The ID of the project.

key\_id

string

Required

The ID of the API key.

### Returns

Confirmation of the key's deletion or an error if the key belonged to a service account

Example request

curl

```bash
1
2
3
curl -X DELETE https://api.openai.com/v1/organization/projects/proj_abc/api_keys/key_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
{
    "object": "organization.project.api_key.deleted",
    "id": "key_abc",
    "deleted": true
}
```

## The project API key object

Represents an individual API key in a project.

object

string

The object type, which is always `organization.project.api_key`

redacted\_value

string

The redacted value of the API key

name

string

The name of the API key

created\_at

integer

The Unix timestamp (in seconds) of when the API key was created

id

string

The identifier, which can be referenced in API endpoints

owner

object

Show properties

OBJECT The project API key object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
{
    "object": "organization.project.api_key",
    "redacted_value": "sk-abc...def",
    "name": "My API Key",
    "created_at": 1711471533,
    "id": "key_abc",
    "owner": {
        "type": "user",
        "user": {
            "object": "organization.project.user",
            "id": "user_abc",
            "name": "First Last",
            "email": "user@example.com",
            "role": "owner",
            "created_at": 1711471533
        }
    }
}
```

## Project rate limits

Manage rate limits per model for projects. Rate limits may be configured to be equal to or lower than the organization's rate limits.

## List project rate limits

gethttps://api.openai.com/v1/organization/projects/{project\_id}/rate\_limits

Returns the rate limits per model for a project.

### Path parameters

project\_id

string

Required

The ID of the project.

### Query parameters

limit

integer

Optional

Defaults to 100

A limit on the number of objects to be returned. The default is 100.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, beginning with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

### Returns

A list of [ProjectRateLimit](https://platform.openai.com/docs/api-reference/project-rate-limits/object) objects.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/projects/proj_abc/rate_limits?after=rl_xxx&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
{
    "object": "list",
    "data": [\
        {\
          "object": "project.rate_limit",\
          "id": "rl-ada",\
          "model": "ada",\
          "max_requests_per_1_minute": 600,\
          "max_tokens_per_1_minute": 150000,\
          "max_images_per_1_minute": 10\
        }\
    ],
    "first_id": "rl-ada",
    "last_id": "rl-ada",
    "has_more": false
}
```

## Modify project rate limit

posthttps://api.openai.com/v1/organization/projects/{project\_id}/rate\_limits/{rate\_limit\_id}

Updates a project rate limit.

### Path parameters

project\_id

string

Required

The ID of the project.

rate\_limit\_id

string

Required

The ID of the rate limit.

### Request body

max\_requests\_per\_1\_minute

integer

Optional

The maximum requests per minute.

max\_tokens\_per\_1\_minute

integer

Optional

The maximum tokens per minute.

max\_images\_per\_1\_minute

integer

Optional

The maximum images per minute. Only relevant for certain models.

max\_audio\_megabytes\_per\_1\_minute

integer

Optional

The maximum audio megabytes per minute. Only relevant for certain models.

max\_requests\_per\_1\_day

integer

Optional

The maximum requests per day. Only relevant for certain models.

batch\_1\_day\_max\_input\_tokens

integer

Optional

The maximum batch input tokens per day. Only relevant for certain models.

### Returns

The updated [ProjectRateLimit](https://platform.openai.com/docs/api-reference/project-rate-limits/object) object.

Example request

curl

```bash
1
2
3
4
5
6
curl -X POST https://api.openai.com/v1/organization/projects/proj_abc/rate_limits/rl_xxx \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "max_requests_per_1_minute": 500
  }'
```

Response

```json
1
2
3
4
5
6
7
8
{
    "object": "project.rate_limit",
    "id": "rl-ada",
    "model": "ada",
    "max_requests_per_1_minute": 600,
    "max_tokens_per_1_minute": 150000,
    "max_images_per_1_minute": 10
  }
```

## The project rate limit object

Represents a project rate limit config.

object

string

The object type, which is always `project.rate_limit`

id

string

The identifier, which can be referenced in API endpoints.

model

string

The model this rate limit applies to.

max\_requests\_per\_1\_minute

integer

The maximum requests per minute.

max\_tokens\_per\_1\_minute

integer

The maximum tokens per minute.

max\_images\_per\_1\_minute

integer

The maximum images per minute. Only present for relevant models.

max\_audio\_megabytes\_per\_1\_minute

integer

The maximum audio megabytes per minute. Only present for relevant models.

max\_requests\_per\_1\_day

integer

The maximum requests per day. Only present for relevant models.

batch\_1\_day\_max\_input\_tokens

integer

The maximum batch input tokens per day. Only present for relevant models.

OBJECT The project rate limit object

```JSON
1
2
3
4
5
6
7
8
{
    "object": "project.rate_limit",
    "id": "rl_ada",
    "model": "ada",
    "max_requests_per_1_minute": 600,
    "max_tokens_per_1_minute": 150000,
    "max_images_per_1_minute": 10
}
```

## Audit logs

Logs of user actions and configuration changes within this organization.
To log events, you must activate logging in the [Organization Settings](https://platform.openai.com/settings/organization/general).
Once activated, for security reasons, logging cannot be deactivated.

## List audit logs

gethttps://api.openai.com/v1/organization/audit\_logs

List user actions and configuration changes within this organization.

### Query parameters

effective\_at

object

Optional

Return only events whose `effective_at` (Unix seconds) is in this range.

Show properties

project\_ids\[\]

array

Optional

Return only events for these projects.

event\_types\[\]

array

Optional

Return only events with a `type` in one of these values. For example, `project.created`. For all options, see the documentation for the [audit log object](https://platform.openai.com/docs/api-reference/audit-logs/object).

actor\_ids\[\]

array

Optional

Return only events performed by these actors. Can be a user ID, a service account ID, or an api key tracking ID.

actor\_emails\[\]

array

Optional

Return only events performed by users with these emails.

resource\_ids\[\]

array

Optional

Return only events performed on these targets. For example, a project ID updated.

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

### Returns

A list of paginated [Audit Log](https://platform.openai.com/docs/api-reference/audit-logs/object) objects.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/organization/audit_logs \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
{
    "object": "list",
    "data": [\
        {\
            "id": "audit_log-xxx_yyyymmdd",\
            "type": "project.archived",\
            "effective_at": 1722461446,\
            "actor": {\
                "type": "api_key",\
                "api_key": {\
                    "type": "user",\
                    "user": {\
                        "id": "user-xxx",\
                        "email": "user@example.com"\
                    }\
                }\
            },\
            "project.archived": {\
                "id": "proj_abc"\
            },\
        },\
        {\
            "id": "audit_log-yyy__20240101",\
            "type": "api_key.updated",\
            "effective_at": 1720804190,\
            "actor": {\
                "type": "session",\
                "session": {\
                    "user": {\
                        "id": "user-xxx",\
                        "email": "user@example.com"\
                    },\
                    "ip_address": "127.0.0.1",\
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",\
                    "ja3": "a497151ce4338a12c4418c44d375173e",\
                    "ja4": "q13d0313h3_55b375c5d22e_c7319ce65786",\
                    "ip_address_details": {\
                      "country": "US",\
                      "city": "San Francisco",\
                      "region": "California",\
                      "region_code": "CA",\
                      "asn": "1234",\
                      "latitude": "37.77490",\
                      "longitude": "-122.41940"\
                    }\
                }\
            },\
            "api_key.updated": {\
                "id": "key_xxxx",\
                "data": {\
                    "scopes": ["resource_2.operation_2"]\
                }\
            },\
        }\
    ],
    "first_id": "audit_log-xxx__20240101",
    "last_id": "audit_log_yyy__20240101",
    "has_more": true
}
```

## The audit log object

A log of a user action or configuration change within this organization.

id

string

The ID of this log.

type

string

The event type.

effective\_at

integer

The Unix timestamp (in seconds) of the event.

project

object

The project that the action was scoped to. Absent for actions not scoped to projects.

Show properties

actor

object

The actor who performed the audit logged action.

Show properties

api\_key.created

object

The details for events with this `type`.

Show properties

api\_key.updated

object

The details for events with this `type`.

Show properties

api\_key.deleted

object

The details for events with this `type`.

Show properties

invite.sent

object

The details for events with this `type`.

Show properties

invite.accepted

object

The details for events with this `type`.

Show properties

invite.deleted

object

The details for events with this `type`.

Show properties

login.failed

object

The details for events with this `type`.

Show properties

logout.failed

object

The details for events with this `type`.

Show properties

organization.updated

object

The details for events with this `type`.

Show properties

project.created

object

The details for events with this `type`.

Show properties

project.updated

object

The details for events with this `type`.

Show properties

project.archived

object

The details for events with this `type`.

Show properties

rate\_limit.updated

object

The details for events with this `type`.

Show properties

rate\_limit.deleted

object

The details for events with this `type`.

Show properties

service\_account.created

object

The details for events with this `type`.

Show properties

service\_account.updated

object

The details for events with this `type`.

Show properties

service\_account.deleted

object

The details for events with this `type`.

Show properties

user.added

object

The details for events with this `type`.

Show properties

user.updated

object

The details for events with this `type`.

Show properties

user.deleted

object

The details for events with this `type`.

Show properties

OBJECT The audit log object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
{
    "id": "req_xxx_20240101",
    "type": "api_key.created",
    "effective_at": 1720804090,
    "actor": {
        "type": "session",
        "session": {
            "user": {
                "id": "user-xxx",
                "email": "user@example.com"
            },
            "ip_address": "127.0.0.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    },
    "api_key.created": {
        "id": "key_xxxx",
        "data": {
            "scopes": ["resource.operation"]
        }
    }
}
```

## Usage

The **Usage API** provides detailed insights into your activity across the OpenAI API. It also includes a separate [Costs endpoint](https://platform.openai.com/docs/api-reference/usage/costs), which offers visibility into your spend, breaking down consumption by invoice line items and project IDs.

While the Usage API delivers granular usage data, it may not always reconcile perfectly with the Costs due to minor differences in how usage and spend are recorded. For financial purposes, we recommend using the [Costs endpoint](https://platform.openai.com/docs/api-reference/usage/costs) or the [Costs tab](https://platform.openai.com/settings/organization/usage) in the Usage Dashboard, which will reconcile back to your billing invoice.

## Completions

gethttps://api.openai.com/v1/organization/usage/completions

Get completions usage details for the organization.

### Query parameters

start\_time

integer

Required

Start time (Unix seconds) of the query time range, inclusive.

end\_time

integer

Optional

End time (Unix seconds) of the query time range, exclusive.

bucket\_width

string

Optional

Defaults to 1d

Width of each time bucket in response. Currently `1m`, `1h` and `1d` are supported, default to `1d`.

project\_ids

array

Optional

Return only usage for these projects.

user\_ids

array

Optional

Return only usage for these users.

api\_key\_ids

array

Optional

Return only usage for these API keys.

models

array

Optional

Return only usage for these models.

batch

boolean

Optional

If `true`, return batch jobs only. If `false`, return non-batch jobs only. By default, return both.

group\_by

array

Optional

Group the usage data by the specified fields. Support fields include `project_id`, `user_id`, `api_key_id`, `model`, `batch` or any combination of them.

limit

integer

Optional

Specifies the number of buckets to return.

- `bucket_width=1d`: default: 7, max: 31
- `bucket_width=1h`: default: 24, max: 168
- `bucket_width=1m`: default: 60, max: 1440

page

string

Optional

A cursor for use in pagination. Corresponding to the `next_page` field from the previous response.

### Returns

A list of paginated, time bucketed [Completions usage](https://platform.openai.com/docs/api-reference/usage/completions_object) objects.

Example request

curl

```bash
1
2
3
curl "https://api.openai.com/v1/organization/usage/completions?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
{
    "object": "page",
    "data": [\
        {\
            "object": "bucket",\
            "start_time": 1730419200,\
            "end_time": 1730505600,\
            "results": [\
                {\
                    "object": "organization.usage.completions.result",\
                    "input_tokens": 1000,\
                    "output_tokens": 500,\
                    "input_cached_tokens": 800,\
                    "input_audio_tokens": 0,\
                    "output_audio_tokens": 0,\
                    "num_model_requests": 5,\
                    "project_id": null,\
                    "user_id": null,\
                    "api_key_id": null,\
                    "model": null,\
                    "batch": null\
                }\
            ]\
        }\
    ],
    "has_more": true,
    "next_page": "page_AAAAAGdGxdEiJdKOAAAAAGcqsYA="
}
```

## Completions usage object

The aggregated completions usage details of the specific time bucket.

object

string

input\_tokens

integer

The aggregated number of text input tokens used, including cached tokens. For customers subscribe to scale tier, this includes scale tier tokens.

input\_cached\_tokens

integer

The aggregated number of text input tokens that has been cached from previous requests. For customers subscribe to scale tier, this includes scale tier tokens.

output\_tokens

integer

The aggregated number of text output tokens used. For customers subscribe to scale tier, this includes scale tier tokens.

input\_audio\_tokens

integer

The aggregated number of audio input tokens used, including cached tokens.

output\_audio\_tokens

integer

The aggregated number of audio output tokens used.

num\_model\_requests

integer

The count of requests made to the model.

project\_id

string or null

When `group_by=project_id`, this field provides the project ID of the grouped usage result.

user\_id

string or null

When `group_by=user_id`, this field provides the user ID of the grouped usage result.

api\_key\_id

string or null

When `group_by=api_key_id`, this field provides the API key ID of the grouped usage result.

model

string or null

When `group_by=model`, this field provides the model name of the grouped usage result.

batch

boolean or null

When `group_by=batch`, this field tells whether the grouped usage result is batch or not.

OBJECT Completions usage object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
{
    "object": "organization.usage.completions.result",
    "input_tokens": 5000,
    "output_tokens": 1000,
    "input_cached_tokens": 4000,
    "input_audio_tokens": 300,
    "output_audio_tokens": 200,
    "num_model_requests": 5,
    "project_id": "proj_abc",
    "user_id": "user-abc",
    "api_key_id": "key_abc",
    "model": "gpt-4o-mini-2024-07-18",
    "batch": false
}
```

## Embeddings

gethttps://api.openai.com/v1/organization/usage/embeddings

Get embeddings usage details for the organization.

### Query parameters

start\_time

integer

Required

Start time (Unix seconds) of the query time range, inclusive.

end\_time

integer

Optional

End time (Unix seconds) of the query time range, exclusive.

bucket\_width

string

Optional

Defaults to 1d

Width of each time bucket in response. Currently `1m`, `1h` and `1d` are supported, default to `1d`.

project\_ids

array

Optional

Return only usage for these projects.

user\_ids

array

Optional

Return only usage for these users.

api\_key\_ids

array

Optional

Return only usage for these API keys.

models

array

Optional

Return only usage for these models.

group\_by

array

Optional

Group the usage data by the specified fields. Support fields include `project_id`, `user_id`, `api_key_id`, `model` or any combination of them.

limit

integer

Optional

Specifies the number of buckets to return.

- `bucket_width=1d`: default: 7, max: 31
- `bucket_width=1h`: default: 24, max: 168
- `bucket_width=1m`: default: 60, max: 1440

page

string

Optional

A cursor for use in pagination. Corresponding to the `next_page` field from the previous response.

### Returns

A list of paginated, time bucketed [Embeddings usage](https://platform.openai.com/docs/api-reference/usage/embeddings_object) objects.

Example request

curl

```bash
1
2
3
curl "https://api.openai.com/v1/organization/usage/embeddings?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
{
    "object": "page",
    "data": [\
        {\
            "object": "bucket",\
            "start_time": 1730419200,\
            "end_time": 1730505600,\
            "results": [\
                {\
                    "object": "organization.usage.embeddings.result",\
                    "input_tokens": 16,\
                    "num_model_requests": 2,\
                    "project_id": null,\
                    "user_id": null,\
                    "api_key_id": null,\
                    "model": null\
                }\
            ]\
        }\
    ],
    "has_more": false,
    "next_page": null
}
```

## Embeddings usage object

The aggregated embeddings usage details of the specific time bucket.

object

string

input\_tokens

integer

The aggregated number of input tokens used.

num\_model\_requests

integer

The count of requests made to the model.

project\_id

string or null

When `group_by=project_id`, this field provides the project ID of the grouped usage result.

user\_id

string or null

When `group_by=user_id`, this field provides the user ID of the grouped usage result.

api\_key\_id

string or null

When `group_by=api_key_id`, this field provides the API key ID of the grouped usage result.

model

string or null

When `group_by=model`, this field provides the model name of the grouped usage result.

OBJECT Embeddings usage object

```JSON
1
2
3
4
5
6
7
8
9
{
    "object": "organization.usage.embeddings.result",
    "input_tokens": 20,
    "num_model_requests": 2,
    "project_id": "proj_abc",
    "user_id": "user-abc",
    "api_key_id": "key_abc",
    "model": "text-embedding-ada-002-v2"
}
```

## Moderations

gethttps://api.openai.com/v1/organization/usage/moderations

Get moderations usage details for the organization.

### Query parameters

start\_time

integer

Required

Start time (Unix seconds) of the query time range, inclusive.

end\_time

integer

Optional

End time (Unix seconds) of the query time range, exclusive.

bucket\_width

string

Optional

Defaults to 1d

Width of each time bucket in response. Currently `1m`, `1h` and `1d` are supported, default to `1d`.

project\_ids

array

Optional

Return only usage for these projects.

user\_ids

array

Optional

Return only usage for these users.

api\_key\_ids

array

Optional

Return only usage for these API keys.

models

array

Optional

Return only usage for these models.

group\_by

array

Optional

Group the usage data by the specified fields. Support fields include `project_id`, `user_id`, `api_key_id`, `model` or any combination of them.

limit

integer

Optional

Specifies the number of buckets to return.

- `bucket_width=1d`: default: 7, max: 31
- `bucket_width=1h`: default: 24, max: 168
- `bucket_width=1m`: default: 60, max: 1440

page

string

Optional

A cursor for use in pagination. Corresponding to the `next_page` field from the previous response.

### Returns

A list of paginated, time bucketed [Moderations usage](https://platform.openai.com/docs/api-reference/usage/moderations_object) objects.

Example request

curl

```bash
1
2
3
curl "https://api.openai.com/v1/organization/usage/moderations?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
{
    "object": "page",
    "data": [\
        {\
            "object": "bucket",\
            "start_time": 1730419200,\
            "end_time": 1730505600,\
            "results": [\
                {\
                    "object": "organization.usage.moderations.result",\
                    "input_tokens": 16,\
                    "num_model_requests": 2,\
                    "project_id": null,\
                    "user_id": null,\
                    "api_key_id": null,\
                    "model": null\
                }\
            ]\
        }\
    ],
    "has_more": false,
    "next_page": null
}
```

## Moderations usage object

The aggregated moderations usage details of the specific time bucket.

object

string

input\_tokens

integer

The aggregated number of input tokens used.

num\_model\_requests

integer

The count of requests made to the model.

project\_id

string or null

When `group_by=project_id`, this field provides the project ID of the grouped usage result.

user\_id

string or null

When `group_by=user_id`, this field provides the user ID of the grouped usage result.

api\_key\_id

string or null

When `group_by=api_key_id`, this field provides the API key ID of the grouped usage result.

model

string or null

When `group_by=model`, this field provides the model name of the grouped usage result.

OBJECT Moderations usage object

```JSON
1
2
3
4
5
6
7
8
9
{
    "object": "organization.usage.moderations.result",
    "input_tokens": 20,
    "num_model_requests": 2,
    "project_id": "proj_abc",
    "user_id": "user-abc",
    "api_key_id": "key_abc",
    "model": "text-moderation"
}
```

## Images

gethttps://api.openai.com/v1/organization/usage/images

Get images usage details for the organization.

### Query parameters

start\_time

integer

Required

Start time (Unix seconds) of the query time range, inclusive.

end\_time

integer

Optional

End time (Unix seconds) of the query time range, exclusive.

bucket\_width

string

Optional

Defaults to 1d

Width of each time bucket in response. Currently `1m`, `1h` and `1d` are supported, default to `1d`.

sources

array

Optional

Return only usages for these sources. Possible values are `image.generation`, `image.edit`, `image.variation` or any combination of them.

sizes

array

Optional

Return only usages for these image sizes. Possible values are `256x256`, `512x512`, `1024x1024`, `1792x1792`, `1024x1792` or any combination of them.

project\_ids

array

Optional

Return only usage for these projects.

user\_ids

array

Optional

Return only usage for these users.

api\_key\_ids

array

Optional

Return only usage for these API keys.

models

array

Optional

Return only usage for these models.

group\_by

array

Optional

Group the usage data by the specified fields. Support fields include `project_id`, `user_id`, `api_key_id`, `model`, `size`, `source` or any combination of them.

limit

integer

Optional

Specifies the number of buckets to return.

- `bucket_width=1d`: default: 7, max: 31
- `bucket_width=1h`: default: 24, max: 168
- `bucket_width=1m`: default: 60, max: 1440

page

string

Optional

A cursor for use in pagination. Corresponding to the `next_page` field from the previous response.

### Returns

A list of paginated, time bucketed [Images usage](https://platform.openai.com/docs/api-reference/usage/images_object) objects.

Example request

curl

```bash
1
2
3
curl "https://api.openai.com/v1/organization/usage/images?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
{
    "object": "page",
    "data": [\
        {\
            "object": "bucket",\
            "start_time": 1730419200,\
            "end_time": 1730505600,\
            "results": [\
                {\
                    "object": "organization.usage.images.result",\
                    "images": 2,\
                    "num_model_requests": 2,\
                    "size": null,\
                    "source": null,\
                    "project_id": null,\
                    "user_id": null,\
                    "api_key_id": null,\
                    "model": null\
                }\
            ]\
        }\
    ],
    "has_more": false,
    "next_page": null
}
```

## Images usage object

The aggregated images usage details of the specific time bucket.

object

string

images

integer

The number of images processed.

num\_model\_requests

integer

The count of requests made to the model.

source

string or null

When `group_by=source`, this field provides the source of the grouped usage result, possible values are `image.generation`, `image.edit`, `image.variation`.

size

string or null

When `group_by=size`, this field provides the image size of the grouped usage result.

project\_id

string or null

When `group_by=project_id`, this field provides the project ID of the grouped usage result.

user\_id

string or null

When `group_by=user_id`, this field provides the user ID of the grouped usage result.

api\_key\_id

string or null

When `group_by=api_key_id`, this field provides the API key ID of the grouped usage result.

model

string or null

When `group_by=model`, this field provides the model name of the grouped usage result.

OBJECT Images usage object

```JSON
1
2
3
4
5
6
7
8
9
10
11
{
    "object": "organization.usage.images.result",
    "images": 2,
    "num_model_requests": 2,
    "size": "1024x1024",
    "source": "image.generation",
    "project_id": "proj_abc",
    "user_id": "user-abc",
    "api_key_id": "key_abc",
    "model": "dall-e-3"
}
```

## Audio speeches

gethttps://api.openai.com/v1/organization/usage/audio\_speeches

Get audio speeches usage details for the organization.

### Query parameters

start\_time

integer

Required

Start time (Unix seconds) of the query time range, inclusive.

end\_time

integer

Optional

End time (Unix seconds) of the query time range, exclusive.

bucket\_width

string

Optional

Defaults to 1d

Width of each time bucket in response. Currently `1m`, `1h` and `1d` are supported, default to `1d`.

project\_ids

array

Optional

Return only usage for these projects.

user\_ids

array

Optional

Return only usage for these users.

api\_key\_ids

array

Optional

Return only usage for these API keys.

models

array

Optional

Return only usage for these models.

group\_by

array

Optional

Group the usage data by the specified fields. Support fields include `project_id`, `user_id`, `api_key_id`, `model` or any combination of them.

limit

integer

Optional

Specifies the number of buckets to return.

- `bucket_width=1d`: default: 7, max: 31
- `bucket_width=1h`: default: 24, max: 168
- `bucket_width=1m`: default: 60, max: 1440

page

string

Optional

A cursor for use in pagination. Corresponding to the `next_page` field from the previous response.

### Returns

A list of paginated, time bucketed [Audio speeches usage](https://platform.openai.com/docs/api-reference/usage/audio_speeches_object) objects.

Example request

curl

```bash
1
2
3
curl "https://api.openai.com/v1/organization/usage/audio_speeches?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
{
    "object": "page",
    "data": [\
        {\
            "object": "bucket",\
            "start_time": 1730419200,\
            "end_time": 1730505600,\
            "results": [\
                {\
                    "object": "organization.usage.audio_speeches.result",\
                    "characters": 45,\
                    "num_model_requests": 1,\
                    "project_id": null,\
                    "user_id": null,\
                    "api_key_id": null,\
                    "model": null\
                }\
            ]\
        }\
    ],
    "has_more": false,
    "next_page": null
}
```

## Audio speeches usage object

The aggregated audio speeches usage details of the specific time bucket.

object

string

characters

integer

The number of characters processed.

num\_model\_requests

integer

The count of requests made to the model.

project\_id

string or null

When `group_by=project_id`, this field provides the project ID of the grouped usage result.

user\_id

string or null

When `group_by=user_id`, this field provides the user ID of the grouped usage result.

api\_key\_id

string or null

When `group_by=api_key_id`, this field provides the API key ID of the grouped usage result.

model

string or null

When `group_by=model`, this field provides the model name of the grouped usage result.

OBJECT Audio speeches usage object

```JSON
1
2
3
4
5
6
7
8
9
{
    "object": "organization.usage.audio_speeches.result",
    "characters": 45,
    "num_model_requests": 1,
    "project_id": "proj_abc",
    "user_id": "user-abc",
    "api_key_id": "key_abc",
    "model": "tts-1"
}
```

## Audio transcriptions

gethttps://api.openai.com/v1/organization/usage/audio\_transcriptions

Get audio transcriptions usage details for the organization.

### Query parameters

start\_time

integer

Required

Start time (Unix seconds) of the query time range, inclusive.

end\_time

integer

Optional

End time (Unix seconds) of the query time range, exclusive.

bucket\_width

string

Optional

Defaults to 1d

Width of each time bucket in response. Currently `1m`, `1h` and `1d` are supported, default to `1d`.

project\_ids

array

Optional

Return only usage for these projects.

user\_ids

array

Optional

Return only usage for these users.

api\_key\_ids

array

Optional

Return only usage for these API keys.

models

array

Optional

Return only usage for these models.

group\_by

array

Optional

Group the usage data by the specified fields. Support fields include `project_id`, `user_id`, `api_key_id`, `model` or any combination of them.

limit

integer

Optional

Specifies the number of buckets to return.

- `bucket_width=1d`: default: 7, max: 31
- `bucket_width=1h`: default: 24, max: 168
- `bucket_width=1m`: default: 60, max: 1440

page

string

Optional

A cursor for use in pagination. Corresponding to the `next_page` field from the previous response.

### Returns

A list of paginated, time bucketed [Audio transcriptions usage](https://platform.openai.com/docs/api-reference/usage/audio_transcriptions_object) objects.

Example request

curl

```bash
1
2
3
curl "https://api.openai.com/v1/organization/usage/audio_transcriptions?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
{
    "object": "page",
    "data": [\
        {\
            "object": "bucket",\
            "start_time": 1730419200,\
            "end_time": 1730505600,\
            "results": [\
                {\
                    "object": "organization.usage.audio_transcriptions.result",\
                    "seconds": 20,\
                    "num_model_requests": 1,\
                    "project_id": null,\
                    "user_id": null,\
                    "api_key_id": null,\
                    "model": null\
                }\
            ]\
        }\
    ],
    "has_more": false,
    "next_page": null
}
```

## Audio transcriptions usage object

The aggregated audio transcriptions usage details of the specific time bucket.

object

string

seconds

integer

The number of seconds processed.

num\_model\_requests

integer

The count of requests made to the model.

project\_id

string or null

When `group_by=project_id`, this field provides the project ID of the grouped usage result.

user\_id

string or null

When `group_by=user_id`, this field provides the user ID of the grouped usage result.

api\_key\_id

string or null

When `group_by=api_key_id`, this field provides the API key ID of the grouped usage result.

model

string or null

When `group_by=model`, this field provides the model name of the grouped usage result.

OBJECT Audio transcriptions usage object

```JSON
1
2
3
4
5
6
7
8
9
{
    "object": "organization.usage.audio_transcriptions.result",
    "seconds": 10,
    "num_model_requests": 1,
    "project_id": "proj_abc",
    "user_id": "user-abc",
    "api_key_id": "key_abc",
    "model": "tts-1"
}
```

## Vector stores

gethttps://api.openai.com/v1/organization/usage/vector\_stores

Get vector stores usage details for the organization.

### Query parameters

start\_time

integer

Required

Start time (Unix seconds) of the query time range, inclusive.

end\_time

integer

Optional

End time (Unix seconds) of the query time range, exclusive.

bucket\_width

string

Optional

Defaults to 1d

Width of each time bucket in response. Currently `1m`, `1h` and `1d` are supported, default to `1d`.

project\_ids

array

Optional

Return only usage for these projects.

group\_by

array

Optional

Group the usage data by the specified fields. Support fields include `project_id`.

limit

integer

Optional

Specifies the number of buckets to return.

- `bucket_width=1d`: default: 7, max: 31
- `bucket_width=1h`: default: 24, max: 168
- `bucket_width=1m`: default: 60, max: 1440

page

string

Optional

A cursor for use in pagination. Corresponding to the `next_page` field from the previous response.

### Returns

A list of paginated, time bucketed [Vector stores usage](https://platform.openai.com/docs/api-reference/usage/vector_stores_object) objects.

Example request

curl

```bash
1
2
3
curl "https://api.openai.com/v1/organization/usage/vector_stores?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
{
    "object": "page",
    "data": [\
        {\
            "object": "bucket",\
            "start_time": 1730419200,\
            "end_time": 1730505600,\
            "results": [\
                {\
                    "object": "organization.usage.vector_stores.result",\
                    "usage_bytes": 1024,\
                    "project_id": null\
                }\
            ]\
        }\
    ],
    "has_more": false,
    "next_page": null
}
```

## Vector stores usage object

The aggregated vector stores usage details of the specific time bucket.

object

string

usage\_bytes

integer

The vector stores usage in bytes.

project\_id

string or null

When `group_by=project_id`, this field provides the project ID of the grouped usage result.

OBJECT Vector stores usage object

```JSON
1
2
3
4
5
{
    "object": "organization.usage.vector_stores.result",
    "usage_bytes": 1024,
    "project_id": "proj_abc"
}
```

## Code interpreter sessions

gethttps://api.openai.com/v1/organization/usage/code\_interpreter\_sessions

Get code interpreter sessions usage details for the organization.

### Query parameters

start\_time

integer

Required

Start time (Unix seconds) of the query time range, inclusive.

end\_time

integer

Optional

End time (Unix seconds) of the query time range, exclusive.

bucket\_width

string

Optional

Defaults to 1d

Width of each time bucket in response. Currently `1m`, `1h` and `1d` are supported, default to `1d`.

project\_ids

array

Optional

Return only usage for these projects.

group\_by

array

Optional

Group the usage data by the specified fields. Support fields include `project_id`.

limit

integer

Optional

Specifies the number of buckets to return.

- `bucket_width=1d`: default: 7, max: 31
- `bucket_width=1h`: default: 24, max: 168
- `bucket_width=1m`: default: 60, max: 1440

page

string

Optional

A cursor for use in pagination. Corresponding to the `next_page` field from the previous response.

### Returns

A list of paginated, time bucketed [Code interpreter sessions usage](https://platform.openai.com/docs/api-reference/usage/code_interpreter_sessions_object) objects.

Example request

curl

```bash
1
2
3
curl "https://api.openai.com/v1/organization/usage/code_interpreter_sessions?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
{
    "object": "page",
    "data": [\
        {\
            "object": "bucket",\
            "start_time": 1730419200,\
            "end_time": 1730505600,\
            "results": [\
                {\
                    "object": "organization.usage.code_interpreter_sessions.result",\
                    "sessions": 1,\
                    "project_id": null\
                }\
            ]\
        }\
    ],
    "has_more": false,
    "next_page": null
}
```

## Code interpreter sessions usage object

The aggregated code interpreter sessions usage details of the specific time bucket.

object

string

sessions

integer

The number of code interpreter sessions.

project\_id

string or null

When `group_by=project_id`, this field provides the project ID of the grouped usage result.

OBJECT Code interpreter sessions usage object

```JSON
1
2
3
4
5
{
    "object": "organization.usage.code_interpreter_sessions.result",
    "sessions": 1,
    "project_id": "proj_abc"
}
```

## Costs

gethttps://api.openai.com/v1/organization/costs

Get costs details for the organization.

### Query parameters

start\_time

integer

Required

Start time (Unix seconds) of the query time range, inclusive.

end\_time

integer

Optional

End time (Unix seconds) of the query time range, exclusive.

bucket\_width

string

Optional

Defaults to 1d

Width of each time bucket in response. Currently only `1d` is supported, default to `1d`.

project\_ids

array

Optional

Return only costs for these projects.

group\_by

array

Optional

Group the costs by the specified fields. Support fields include `project_id`, `line_item` and any combination of them.

limit

integer

Optional

Defaults to 7

A limit on the number of buckets to be returned. Limit can range between 1 and 180, and the default is 7.

page

string

Optional

A cursor for use in pagination. Corresponding to the `next_page` field from the previous response.

### Returns

A list of paginated, time bucketed [Costs](https://platform.openai.com/docs/api-reference/usage/costs_object) objects.

Example request

curl

```bash
1
2
3
curl "https://api.openai.com/v1/organization/costs?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
{
    "object": "page",
    "data": [\
        {\
            "object": "bucket",\
            "start_time": 1730419200,\
            "end_time": 1730505600,\
            "results": [\
                {\
                    "object": "organization.costs.result",\
                    "amount": {\
                        "value": 0.06,\
                        "currency": "usd"\
                    },\
                    "line_item": null,\
                    "project_id": null\
                }\
            ]\
        }\
    ],
    "has_more": false,
    "next_page": null
}
```

## Costs object

The aggregated costs details of the specific time bucket.

object

string

amount

object

The monetary value in its associated currency.

Show properties

line\_item

string or null

When `group_by=line_item`, this field provides the line item of the grouped costs result.

project\_id

string or null

When `group_by=project_id`, this field provides the project ID of the grouped costs result.

OBJECT Costs object

```JSON
1
2
3
4
5
6
7
8
9
{
    "object": "organization.costs.result",
    "amount": {
      "value": 0.06,
      "currency": "usd"
    },
    "line_item": "Image models",
    "project_id": "proj_abc"
}
```

## Realtime  Beta

Communicate with a GPT-4o class model in real time using WebRTC or
WebSockets. Supports text and audio inputs and ouputs, along with audio
transcriptions.
[Learn more about the Realtime API](https://platform.openai.com/docs/guides/realtime).

## Session tokens

REST API endpoint to generate ephemeral session tokens for use in client-side
applications.

## Create session

posthttps://api.openai.com/v1/realtime/sessions

Create an ephemeral API token for use in client-side applications with the
Realtime API. Can be configured with the same session parameters as the
`session.update` client event.

It responds with a session object, plus a `client_secret` key which contains
a usable ephemeral API token that can be used to authenticate browser clients
for the Realtime API.

### Request body

modalities

Optional

The set of modalities the model can respond with. To disable audio,
set this to \["text"\].

model

string

Optional

The Realtime model used for this session.

instructions

string

Optional

The default system instructions (i.e. system message) prepended to model
calls. This field allows the client to guide the model on desired
responses. The model can be instructed on response content and format,
(e.g. "be extremely succinct", "act friendly", "here are examples of good
responses") and on audio behavior (e.g. "talk quickly", "inject emotion
into your voice", "laugh frequently"). The instructions are not guaranteed
to be followed by the model, but they provide guidance to the model on the
desired behavior.

Note that the server sets default instructions which will be used if this
field is not set and are visible in the `session.created` event at the
start of the session.

voice

string

Optional

The voice the model uses to respond. Voice cannot be changed during the
session once the model has responded with audio at least once. Current
voice options are `alloy`, `ash`, `ballad`, `coral`, `echo` `sage`,
`shimmer` and `verse`.

input\_audio\_format

string

Optional

The format of input audio. Options are `pcm16`, `g711_ulaw`, or `g711_alaw`.
For `pcm16`, input audio must be 16-bit PCM at a 24kHz sample rate,
single channel (mono), and little-endian byte order.

output\_audio\_format

string

Optional

The format of output audio. Options are `pcm16`, `g711_ulaw`, or `g711_alaw`.
For `pcm16`, output audio is sampled at a rate of 24kHz.

input\_audio\_transcription

object

Optional

Configuration for input audio transcription, defaults to off and can be set to `null` to turn off once on. Input audio transcription is not native to the model, since the model consumes audio directly. Transcription runs asynchronously through [OpenAI Whisper transcription](https://platform.openai.com/docs/api-reference/audio/createTranscription) and should be treated as rough guidance rather than the representation understood by the model. The client can optionally set the language and prompt for transcription, these fields will be passed to the Whisper API.

Show properties

turn\_detection

object

Optional

Configuration for turn detection. Can be set to `null` to turn off. Server
VAD means that the model will detect the start and end of speech based on
audio volume and respond at the end of user speech.

Show properties

tools

array

Optional

Tools (functions) available to the model.

Show properties

tool\_choice

string

Optional

How the model chooses tools. Options are `auto`, `none`, `required`, or
specify a function.

temperature

number

Optional

Sampling temperature for the model, limited to \[0.6, 1.2\]. Defaults to 0.8.

max\_response\_output\_tokens

integer or "inf"

Optional

Maximum number of output tokens for a single assistant response,
inclusive of tool calls. Provide an integer between 1 and 4096 to
limit output tokens, or `inf` for the maximum available tokens for a
given model. Defaults to `inf`.

### Returns

The created Realtime session object, plus an ephemeral key

Example request

curl

```bash
1
2
3
4
5
6
7
8
curl -X POST https://api.openai.com/v1/realtime/sessions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-realtime-preview-2024-12-17",
    "modalities": ["audio", "text"],
    "instructions": "You are a friendly assistant."
  }'
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
{
  "id": "sess_001",
  "object": "realtime.session",
  "model": "gpt-4o-realtime-preview-2024-12-17",
  "modalities": ["audio", "text"],
  "instructions": "You are a friendly assistant.",
  "voice": "alloy",
  "input_audio_format": "pcm16",
  "output_audio_format": "pcm16",
  "input_audio_transcription": {
      "model": "whisper-1"
  },
  "turn_detection": null,
  "tools": [],
  "tool_choice": "none",
  "temperature": 0.7,
  "max_response_output_tokens": 200,
  "client_secret": {
    "value": "ek_abc123",
    "expires_at": 1234567890
  }
}
```

## The session object

A new Realtime session configuration, with an ephermeral key. Default TTL
for keys is one minute.

client\_secret

object

Ephemeral key returned by the API.

Show properties

modalities

The set of modalities the model can respond with. To disable audio,
set this to \["text"\].

instructions

string

The default system instructions (i.e. system message) prepended to model
calls. This field allows the client to guide the model on desired
responses. The model can be instructed on response content and format,
(e.g. "be extremely succinct", "act friendly", "here are examples of good
responses") and on audio behavior (e.g. "talk quickly", "inject emotion
into your voice", "laugh frequently"). The instructions are not guaranteed
to be followed by the model, but they provide guidance to the model on the
desired behavior.

Note that the server sets default instructions which will be used if this
field is not set and are visible in the `session.created` event at the
start of the session.

voice

string

The voice the model uses to respond. Voice cannot be changed during the
session once the model has responded with audio at least once. Current
voice options are `alloy`, `ash`, `ballad`, `coral`, `echo` `sage`,
`shimmer` and `verse`.

input\_audio\_format

string

The format of input audio. Options are `pcm16`, `g711_ulaw`, or `g711_alaw`.

output\_audio\_format

string

The format of output audio. Options are `pcm16`, `g711_ulaw`, or `g711_alaw`.

input\_audio\_transcription

object

Configuration for input audio transcription, defaults to off and can be
set to `null` to turn off once on. Input audio transcription is not native
to the model, since the model consumes audio directly. Transcription runs
asynchronously through Whisper and should be treated as rough guidance
rather than the representation understood by the model.

Show properties

turn\_detection

object

Configuration for turn detection. Can be set to `null` to turn off. Server
VAD means that the model will detect the start and end of speech based on
audio volume and respond at the end of user speech.

Show properties

tools

array

Tools (functions) available to the model.

Show properties

tool\_choice

string

How the model chooses tools. Options are `auto`, `none`, `required`, or
specify a function.

temperature

number

Sampling temperature for the model, limited to \[0.6, 1.2\]. Defaults to 0.8.

max\_response\_output\_tokens

integer or "inf"

Maximum number of output tokens for a single assistant response,
inclusive of tool calls. Provide an integer between 1 and 4096 to
limit output tokens, or `inf` for the maximum available tokens for a
given model. Defaults to `inf`.

OBJECT The session object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
{
  "id": "sess_001",
  "object": "realtime.session",
  "model": "gpt-4o-realtime-preview-2024-12-17",
  "modalities": ["audio", "text"],
  "instructions": "You are a friendly assistant.",
  "voice": "alloy",
  "input_audio_format": "pcm16",
  "output_audio_format": "pcm16",
  "input_audio_transcription": {
      "model": "whisper-1"
  },
  "turn_detection": null,
  "tools": [],
  "tool_choice": "none",
  "temperature": 0.7,
  "max_response_output_tokens": 200,
  "client_secret": {
    "value": "ek_abc123",
    "expires_at": 1234567890
  }
}
```

## Client events

These are events that the OpenAI Realtime WebSocket server will accept from the client.

## session.update

Send this event to update the session’s default configuration. The client may
send this event at any time to update the session configuration, and any
field may be updated at any time, except for "voice". The server will respond
with a `session.updated` event that shows the full effective configuration.
Only fields that are present are updated, thus the correct way to clear a
field like "instructions" is to pass an empty string.

event\_id

string

Optional client-generated ID used to identify this event.

type

string

The event type, must be `session.update`.

session

object

Realtime session object configuration.

Show properties

OBJECT session.update

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
{
    "event_id": "event_123",
    "type": "session.update",
    "session": {
        "modalities": ["text", "audio"],
        "instructions": "You are a helpful assistant.",
        "voice": "sage",
        "input_audio_format": "pcm16",
        "output_audio_format": "pcm16",
        "input_audio_transcription": {
            "model": "whisper-1"
        },
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 500,
            "create_response": true
        },
        "tools": [\
            {\
                "type": "function",\
                "name": "get_weather",\
                "description": "Get the current weather...",\
                "parameters": {\
                    "type": "object",\
                    "properties": {\
                        "location": { "type": "string" }\
                    },\
                    "required": ["location"]\
                }\
            }\
        ],
        "tool_choice": "auto",
        "temperature": 0.8,
        "max_response_output_tokens": "inf"
    }
}
```

## input\_audio\_buffer.append

Send this event to append audio bytes to the input audio buffer. The audio
buffer is temporary storage you can write to and later commit. In Server VAD
mode, the audio buffer is used to detect speech and the server will decide
when to commit. When Server VAD is disabled, you must commit the audio buffer
manually.

The client may choose how much audio to place in each event up to a maximum
of 15 MiB, for example streaming smaller chunks from the client may allow the
VAD to be more responsive. Unlike made other client events, the server will
not send a confirmation response to this event.

event\_id

string

Optional client-generated ID used to identify this event.

type

string

The event type, must be `input_audio_buffer.append`.

audio

string

Base64-encoded audio bytes. This must be in the format specified by the
`input_audio_format` field in the session configuration.

OBJECT input\_audio\_buffer.append

```JSON
1
2
3
4
5
{
    "event_id": "event_456",
    "type": "input_audio_buffer.append",
    "audio": "Base64EncodedAudioData"
}
```

## input\_audio\_buffer.commit

Send this event to commit the user input audio buffer, which will create a
new user message item in the conversation. This event will produce an error
if the input audio buffer is empty. When in Server VAD mode, the client does
not need to send this event, the server will commit the audio buffer
automatically.

Committing the input audio buffer will trigger input audio transcription
(if enabled in session configuration), but it will not create a response
from the model. The server will respond with an `input_audio_buffer.committed`
event.

event\_id

string

Optional client-generated ID used to identify this event.

type

string

The event type, must be `input_audio_buffer.commit`.

OBJECT input\_audio\_buffer.commit

```JSON
1
2
3
4
{
    "event_id": "event_789",
    "type": "input_audio_buffer.commit"
}
```

## input\_audio\_buffer.clear

Send this event to clear the audio bytes in the buffer. The server will
respond with an `input_audio_buffer.cleared` event.

event\_id

string

Optional client-generated ID used to identify this event.

type

string

The event type, must be `input_audio_buffer.clear`.

OBJECT input\_audio\_buffer.clear

```JSON
1
2
3
4
{
    "event_id": "event_012",
    "type": "input_audio_buffer.clear"
}
```

## conversation.item.create

Add a new Item to the Conversation's context, including messages, function
calls, and function call responses. This event can be used both to populate a
"history" of the conversation and to add new items mid-stream, but has the
current limitation that it cannot populate assistant audio messages.

If successful, the server will respond with a `conversation.item.created`
event, otherwise an `error` event will be sent.

event\_id

string

Optional client-generated ID used to identify this event.

type

string

The event type, must be `conversation.item.create`.

previous\_item\_id

string

The ID of the preceding item after which the new item will be inserted.
If not set, the new item will be appended to the end of the conversation.
If set to `root`, the new item will be added to the beginning of the conversation.
If set to an existing ID, it allows an item to be inserted mid-conversation. If the
ID cannot be found, an error will be returned and the item will not be added.

item

object

The item to add to the conversation.

Show properties

OBJECT conversation.item.create

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
{
    "event_id": "event_345",
    "type": "conversation.item.create",
    "previous_item_id": null,
    "item": {
        "id": "msg_001",
        "type": "message",
        "role": "user",
        "content": [\
            {\
                "type": "input_text",\
                "text": "Hello, how are you?"\
            }\
        ]
    }
}
```

## conversation.item.truncate

Send this event to truncate a previous assistant message’s audio. The server
will produce audio faster than realtime, so this event is useful when the user
interrupts to truncate audio that has already been sent to the client but not
yet played. This will synchronize the server's understanding of the audio with
the client's playback.

Truncating audio will delete the server-side text transcript to ensure there
is not text in the context that hasn't been heard by the user.

If successful, the server will respond with a `conversation.item.truncated`
event.

event\_id

string

Optional client-generated ID used to identify this event.

type

string

The event type, must be `conversation.item.truncate`.

item\_id

string

The ID of the assistant message item to truncate. Only assistant message
items can be truncated.

content\_index

integer

The index of the content part to truncate. Set this to 0.

audio\_end\_ms

integer

Inclusive duration up to which audio is truncated, in milliseconds. If
the audio\_end\_ms is greater than the actual audio duration, the server
will respond with an error.

OBJECT conversation.item.truncate

```JSON
1
2
3
4
5
6
7
{
    "event_id": "event_678",
    "type": "conversation.item.truncate",
    "item_id": "msg_002",
    "content_index": 0,
    "audio_end_ms": 1500
}
```

## conversation.item.delete

Send this event when you want to remove any item from the conversation
history. The server will respond with a `conversation.item.deleted` event,
unless the item does not exist in the conversation history, in which case the
server will respond with an error.

event\_id

string

Optional client-generated ID used to identify this event.

type

string

The event type, must be `conversation.item.delete`.

item\_id

string

The ID of the item to delete.

OBJECT conversation.item.delete

```JSON
1
2
3
4
5
{
    "event_id": "event_901",
    "type": "conversation.item.delete",
    "item_id": "msg_003"
}
```

## response.create

This event instructs the server to create a Response, which means triggering
model inference. When in Server VAD mode, the server will create Responses
automatically.

A Response will include at least one Item, and may have two, in which case
the second will be a function call. These Items will be appended to the
conversation history.

The server will respond with a `response.created` event, events for Items
and content created, and finally a `response.done` event to indicate the
Response is complete.

The `response.create` event includes inference configuration like
`instructions`, and `temperature`. These fields will override the Session's
configuration for this Response only.

event\_id

string

Optional client-generated ID used to identify this event.

type

string

The event type, must be `response.create`.

response

object

Create a new Realtime response with these parameters

Show properties

OBJECT response.create

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
{
    "event_id": "event_234",
    "type": "response.create",
    "response": {
        "modalities": ["text", "audio"],
        "instructions": "Please assist the user.",
        "voice": "sage",
        "output_audio_format": "pcm16",
        "tools": [\
            {\
                "type": "function",\
                "name": "calculate_sum",\
                "description": "Calculates the sum of two numbers.",\
                "parameters": {\
                    "type": "object",\
                    "properties": {\
                        "a": { "type": "number" },\
                        "b": { "type": "number" }\
                    },\
                    "required": ["a", "b"]\
                }\
            }\
        ],
        "tool_choice": "auto",
        "temperature": 0.8,
        "max_output_tokens": 1024
    }
}
```

## response.cancel

Send this event to cancel an in-progress response. The server will respond
with a `response.cancelled` event or an error if there is no response to
cancel.

event\_id

string

Optional client-generated ID used to identify this event.

type

string

The event type, must be `response.cancel`.

response\_id

string

A specific response ID to cancel - if not provided, will cancel an
in-progress response in the default conversation.

OBJECT response.cancel

```JSON
1
2
3
4
{
    "event_id": "event_567",
    "type": "response.cancel"
}
```

## Server events

These are events emitted from the OpenAI Realtime WebSocket server to the client.

## error

Returned when an error occurs, which could be a client problem or a server
problem. Most errors are recoverable and the session will stay open, we
recommend to implementors to monitor and log error messages by default.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `error`.

error

object

Details of the error.

Show properties

OBJECT error

```JSON
1
2
3
4
5
6
7
8
9
10
11
{
    "event_id": "event_890",
    "type": "error",
    "error": {
        "type": "invalid_request_error",
        "code": "invalid_event",
        "message": "The 'type' field is missing.",
        "param": null,
        "event_id": "event_567"
    }
}
```

## session.created

Returned when a Session is created. Emitted automatically when a new
connection is established as the first server event. This event will contain
the default Session configuration.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `session.created`.

session

object

Realtime session object configuration.

Show properties

OBJECT session.created

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
{
    "event_id": "event_1234",
    "type": "session.created",
    "session": {
        "id": "sess_001",
        "object": "realtime.session",
        "model": "gpt-4o-realtime-preview-2024-12-17",
        "modalities": ["text", "audio"],
        "instructions": "...model instructions here...",
        "voice": "sage",
        "input_audio_format": "pcm16",
        "output_audio_format": "pcm16",
        "input_audio_transcription": null,
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 200
        },
        "tools": [],
        "tool_choice": "auto",
        "temperature": 0.8,
        "max_response_output_tokens": "inf"
    }
}
```

## session.updated

Returned when a session is updated with a `session.update` event, unless
there is an error.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `session.updated`.

session

object

Realtime session object configuration.

Show properties

OBJECT session.updated

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
{
    "event_id": "event_5678",
    "type": "session.updated",
    "session": {
        "id": "sess_001",
        "object": "realtime.session",
        "model": "gpt-4o-realtime-preview-2024-12-17",
        "modalities": ["text"],
        "instructions": "New instructions",
        "voice": "sage",
        "input_audio_format": "pcm16",
        "output_audio_format": "pcm16",
        "input_audio_transcription": {
            "model": "whisper-1"
        },
        "turn_detection": null,
        "tools": [],
        "tool_choice": "none",
        "temperature": 0.7,
        "max_response_output_tokens": 200
    }
}
```

## conversation.created

Returned when a conversation is created. Emitted right after session creation.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `conversation.created`.

conversation

object

The conversation resource.

Show properties

OBJECT conversation.created

```JSON
1
2
3
4
5
6
7
8
{
    "event_id": "event_9101",
    "type": "conversation.created",
    "conversation": {
        "id": "conv_001",
        "object": "realtime.conversation"
    }
}
```

## conversation.item.created

Returned when a conversation item is created. There are several scenarios that
produce this event:

- The server is generating a Response, which if successful will produce
either one or two Items, which will be of type `message`
(role `assistant`) or type `function_call`.
- The input audio buffer has been committed, either by the client or the
server (in `server_vad` mode). The server will take the content of the
input audio buffer and add it to a new user message Item.
- The client has sent a `conversation.item.create` event to add a new Item
to the Conversation.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `conversation.item.created`.

previous\_item\_id

string

The ID of the preceding item in the Conversation context, allows the
client to understand the order of the conversation.

item

object

The item to add to the conversation.

Show properties

OBJECT conversation.item.created

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
{
    "event_id": "event_1920",
    "type": "conversation.item.created",
    "previous_item_id": "msg_002",
    "item": {
        "id": "msg_003",
        "object": "realtime.item",
        "type": "message",
        "status": "completed",
        "role": "user",
        "content": [\
            {\
                "type": "input_audio",\
                "transcript": "hello how are you",\
                "audio": "base64encodedaudio=="\
            }\
        ]
    }
}
```

## conversation.item.input\_audio\_transcription.completed

This event is the output of audio transcription for user audio written to the
user audio buffer. Transcription begins when the input audio buffer is
committed by the client or server (in `server_vad` mode). Transcription runs
asynchronously with Response creation, so this event may come before or after
the Response events.

Realtime API models accept audio natively, and thus input transcription is a
separate process run on a separate ASR (Automatic Speech Recognition) model,
currently always `whisper-1`. Thus the transcript may diverge somewhat from
the model's interpretation, and should be treated as a rough guide.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be
`conversation.item.input_audio_transcription.completed`.

item\_id

string

The ID of the user message item containing the audio.

content\_index

integer

The index of the content part containing the audio.

transcript

string

The transcribed text.

OBJECT conversation.item.input\_audio\_transcription.completed

```JSON
1
2
3
4
5
6
7
{
    "event_id": "event_2122",
    "type": "conversation.item.input_audio_transcription.completed",
    "item_id": "msg_003",
    "content_index": 0,
    "transcript": "Hello, how are you?"
}
```

## conversation.item.input\_audio\_transcription.failed

Returned when input audio transcription is configured, and a transcription
request for a user message failed. These events are separate from other
`error` events so that the client can identify the related Item.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be
`conversation.item.input_audio_transcription.failed`.

item\_id

string

The ID of the user message item.

content\_index

integer

The index of the content part containing the audio.

error

object

Details of the transcription error.

Show properties

OBJECT conversation.item.input\_audio\_transcription.failed

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
{
    "event_id": "event_2324",
    "type": "conversation.item.input_audio_transcription.failed",
    "item_id": "msg_003",
    "content_index": 0,
    "error": {
        "type": "transcription_error",
        "code": "audio_unintelligible",
        "message": "The audio could not be transcribed.",
        "param": null
    }
}
```

## conversation.item.truncated

Returned when an earlier assistant audio message item is truncated by the
client with a `conversation.item.truncate` event. This event is used to
synchronize the server's understanding of the audio with the client's playback.

This action will truncate the audio and remove the server-side text transcript
to ensure there is no text in the context that hasn't been heard by the user.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `conversation.item.truncated`.

item\_id

string

The ID of the assistant message item that was truncated.

content\_index

integer

The index of the content part that was truncated.

audio\_end\_ms

integer

The duration up to which the audio was truncated, in milliseconds.

OBJECT conversation.item.truncated

```JSON
1
2
3
4
5
6
7
{
    "event_id": "event_2526",
    "type": "conversation.item.truncated",
    "item_id": "msg_004",
    "content_index": 0,
    "audio_end_ms": 1500
}
```

## conversation.item.deleted

Returned when an item in the conversation is deleted by the client with a
`conversation.item.delete` event. This event is used to synchronize the
server's understanding of the conversation history with the client's view.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `conversation.item.deleted`.

item\_id

string

The ID of the item that was deleted.

OBJECT conversation.item.deleted

```JSON
1
2
3
4
5
{
    "event_id": "event_2728",
    "type": "conversation.item.deleted",
    "item_id": "msg_005"
}
```

## input\_audio\_buffer.committed

Returned when an input audio buffer is committed, either by the client or
automatically in server VAD mode. The `item_id` property is the ID of the user
message item that will be created, thus a `conversation.item.created` event
will also be sent to the client.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `input_audio_buffer.committed`.

previous\_item\_id

string

The ID of the preceding item after which the new item will be inserted.

item\_id

string

The ID of the user message item that will be created.

OBJECT input\_audio\_buffer.committed

```JSON
1
2
3
4
5
6
{
    "event_id": "event_1121",
    "type": "input_audio_buffer.committed",
    "previous_item_id": "msg_001",
    "item_id": "msg_002"
}
```

## input\_audio\_buffer.cleared

Returned when the input audio buffer is cleared by the client with a
`input_audio_buffer.clear` event.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `input_audio_buffer.cleared`.

OBJECT input\_audio\_buffer.cleared

```JSON
1
2
3
4
{
    "event_id": "event_1314",
    "type": "input_audio_buffer.cleared"
}
```

## input\_audio\_buffer.speech\_started

Sent by the server when in `server_vad` mode to indicate that speech has been
detected in the audio buffer. This can happen any time audio is added to the
buffer (unless speech is already detected). The client may want to use this
event to interrupt audio playback or provide visual feedback to the user.

The client should expect to receive a `input_audio_buffer.speech_stopped` event
when speech stops. The `item_id` property is the ID of the user message item
that will be created when speech stops and will also be included in the
`input_audio_buffer.speech_stopped` event (unless the client manually commits
the audio buffer during VAD activation).

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `input_audio_buffer.speech_started`.

audio\_start\_ms

integer

Milliseconds from the start of all audio written to the buffer during the
session when speech was first detected. This will correspond to the
beginning of audio sent to the model, and thus includes the
`prefix_padding_ms` configured in the Session.

item\_id

string

The ID of the user message item that will be created when speech stops.

OBJECT input\_audio\_buffer.speech\_started

```JSON
1
2
3
4
5
6
{
    "event_id": "event_1516",
    "type": "input_audio_buffer.speech_started",
    "audio_start_ms": 1000,
    "item_id": "msg_003"
}
```

## input\_audio\_buffer.speech\_stopped

Returned in `server_vad` mode when the server detects the end of speech in
the audio buffer. The server will also send an `conversation.item.created`
event with the user message item that is created from the audio buffer.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `input_audio_buffer.speech_stopped`.

audio\_end\_ms

integer

Milliseconds since the session started when speech stopped. This will
correspond to the end of audio sent to the model, and thus includes the
`min_silence_duration_ms` configured in the Session.

item\_id

string

The ID of the user message item that will be created.

OBJECT input\_audio\_buffer.speech\_stopped

```JSON
1
2
3
4
5
6
{
    "event_id": "event_1718",
    "type": "input_audio_buffer.speech_stopped",
    "audio_end_ms": 2000,
    "item_id": "msg_003"
}
```

## response.created

Returned when a new Response is created. The first event of response creation,
where the response is in an initial state of `in_progress`.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.created`.

response

object

The response resource.

Show properties

OBJECT response.created

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
{
    "event_id": "event_2930",
    "type": "response.created",
    "response": {
        "id": "resp_001",
        "object": "realtime.response",
        "status": "in_progress",
        "status_details": null,
        "output": [],
        "usage": null
    }
}
```

## response.done

Returned when a Response is done streaming. Always emitted, no matter the
final state. The Response object included in the `response.done` event will
include all output Items in the Response but will omit the raw audio data.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.done`.

response

object

The response resource.

Show properties

OBJECT response.done

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
{
    "event_id": "event_3132",
    "type": "response.done",
    "response": {
        "id": "resp_001",
        "object": "realtime.response",
        "status": "completed",
        "status_details": null,
        "output": [\
            {\
                "id": "msg_006",\
                "object": "realtime.item",\
                "type": "message",\
                "status": "completed",\
                "role": "assistant",\
                "content": [\
                    {\
                        "type": "text",\
                        "text": "Sure, how can I assist you today?"\
                    }\
                ]\
            }\
        ],
        "usage": {
            "total_tokens":275,
            "input_tokens":127,
            "output_tokens":148,
            "input_token_details": {
                "cached_tokens":384,
                "text_tokens":119,
                "audio_tokens":8,
                "cached_tokens_details": {
                    "text_tokens": 128,
                    "audio_tokens": 256
                }
            },
            "output_token_details": {
              "text_tokens":36,
              "audio_tokens":112
            }
        }
    }
}
```

## response.output\_item.added

Returned when a new Item is created during Response generation.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.output_item.added`.

response\_id

string

The ID of the Response to which the item belongs.

output\_index

integer

The index of the output item in the Response.

item

object

The item to add to the conversation.

Show properties

OBJECT response.output\_item.added

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
{
    "event_id": "event_3334",
    "type": "response.output_item.added",
    "response_id": "resp_001",
    "output_index": 0,
    "item": {
        "id": "msg_007",
        "object": "realtime.item",
        "type": "message",
        "status": "in_progress",
        "role": "assistant",
        "content": []
    }
}
```

## response.output\_item.done

Returned when an Item is done streaming. Also emitted when a Response is
interrupted, incomplete, or cancelled.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.output_item.done`.

response\_id

string

The ID of the Response to which the item belongs.

output\_index

integer

The index of the output item in the Response.

item

object

The item to add to the conversation.

Show properties

OBJECT response.output\_item.done

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
{
    "event_id": "event_3536",
    "type": "response.output_item.done",
    "response_id": "resp_001",
    "output_index": 0,
    "item": {
        "id": "msg_007",
        "object": "realtime.item",
        "type": "message",
        "status": "completed",
        "role": "assistant",
        "content": [\
            {\
                "type": "text",\
                "text": "Sure, I can help with that."\
            }\
        ]
    }
}
```

## response.content\_part.added

Returned when a new content part is added to an assistant message item during
response generation.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.content_part.added`.

response\_id

string

The ID of the response.

item\_id

string

The ID of the item to which the content part was added.

output\_index

integer

The index of the output item in the response.

content\_index

integer

The index of the content part in the item's content array.

part

object

The content part that was added.

Show properties

OBJECT response.content\_part.added

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
{
    "event_id": "event_3738",
    "type": "response.content_part.added",
    "response_id": "resp_001",
    "item_id": "msg_007",
    "output_index": 0,
    "content_index": 0,
    "part": {
        "type": "text",
        "text": ""
    }
}
```

## response.content\_part.done

Returned when a content part is done streaming in an assistant message item.
Also emitted when a Response is interrupted, incomplete, or cancelled.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.content_part.done`.

response\_id

string

The ID of the response.

item\_id

string

The ID of the item.

output\_index

integer

The index of the output item in the response.

content\_index

integer

The index of the content part in the item's content array.

part

object

The content part that is done.

Show properties

OBJECT response.content\_part.done

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
{
    "event_id": "event_3940",
    "type": "response.content_part.done",
    "response_id": "resp_001",
    "item_id": "msg_007",
    "output_index": 0,
    "content_index": 0,
    "part": {
        "type": "text",
        "text": "Sure, I can help with that."
    }
}
```

## response.text.delta

Returned when the text value of a "text" content part is updated.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.text.delta`.

response\_id

string

The ID of the response.

item\_id

string

The ID of the item.

output\_index

integer

The index of the output item in the response.

content\_index

integer

The index of the content part in the item's content array.

delta

string

The text delta.

OBJECT response.text.delta

```JSON
1
2
3
4
5
6
7
8
9
{
    "event_id": "event_4142",
    "type": "response.text.delta",
    "response_id": "resp_001",
    "item_id": "msg_007",
    "output_index": 0,
    "content_index": 0,
    "delta": "Sure, I can h"
}
```

## response.text.done

Returned when the text value of a "text" content part is done streaming. Also
emitted when a Response is interrupted, incomplete, or cancelled.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.text.done`.

response\_id

string

The ID of the response.

item\_id

string

The ID of the item.

output\_index

integer

The index of the output item in the response.

content\_index

integer

The index of the content part in the item's content array.

text

string

The final text content.

OBJECT response.text.done

```JSON
1
2
3
4
5
6
7
8
9
{
    "event_id": "event_4344",
    "type": "response.text.done",
    "response_id": "resp_001",
    "item_id": "msg_007",
    "output_index": 0,
    "content_index": 0,
    "text": "Sure, I can help with that."
}
```

## response.audio\_transcript.delta

Returned when the model-generated transcription of audio output is updated.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.audio_transcript.delta`.

response\_id

string

The ID of the response.

item\_id

string

The ID of the item.

output\_index

integer

The index of the output item in the response.

content\_index

integer

The index of the content part in the item's content array.

delta

string

The transcript delta.

OBJECT response.audio\_transcript.delta

```JSON
1
2
3
4
5
6
7
8
9
{
    "event_id": "event_4546",
    "type": "response.audio_transcript.delta",
    "response_id": "resp_001",
    "item_id": "msg_008",
    "output_index": 0,
    "content_index": 0,
    "delta": "Hello, how can I a"
}
```

## response.audio\_transcript.done

Returned when the model-generated transcription of audio output is done
streaming. Also emitted when a Response is interrupted, incomplete, or
cancelled.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.audio_transcript.done`.

response\_id

string

The ID of the response.

item\_id

string

The ID of the item.

output\_index

integer

The index of the output item in the response.

content\_index

integer

The index of the content part in the item's content array.

transcript

string

The final transcript of the audio.

OBJECT response.audio\_transcript.done

```JSON
1
2
3
4
5
6
7
8
9
{
    "event_id": "event_4748",
    "type": "response.audio_transcript.done",
    "response_id": "resp_001",
    "item_id": "msg_008",
    "output_index": 0,
    "content_index": 0,
    "transcript": "Hello, how can I assist you today?"
}
```

## response.audio.delta

Returned when the model-generated audio is updated.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.audio.delta`.

response\_id

string

The ID of the response.

item\_id

string

The ID of the item.

output\_index

integer

The index of the output item in the response.

content\_index

integer

The index of the content part in the item's content array.

delta

string

Base64-encoded audio data delta.

OBJECT response.audio.delta

```JSON
1
2
3
4
5
6
7
8
9
{
    "event_id": "event_4950",
    "type": "response.audio.delta",
    "response_id": "resp_001",
    "item_id": "msg_008",
    "output_index": 0,
    "content_index": 0,
    "delta": "Base64EncodedAudioDelta"
}
```

## response.audio.done

Returned when the model-generated audio is done. Also emitted when a Response
is interrupted, incomplete, or cancelled.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.audio.done`.

response\_id

string

The ID of the response.

item\_id

string

The ID of the item.

output\_index

integer

The index of the output item in the response.

content\_index

integer

The index of the content part in the item's content array.

OBJECT response.audio.done

```JSON
1
2
3
4
5
6
7
8
{
    "event_id": "event_5152",
    "type": "response.audio.done",
    "response_id": "resp_001",
    "item_id": "msg_008",
    "output_index": 0,
    "content_index": 0
}
```

## response.function\_call\_arguments.delta

Returned when the model-generated function call arguments are updated.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.function_call_arguments.delta`.

response\_id

string

The ID of the response.

item\_id

string

The ID of the function call item.

output\_index

integer

The index of the output item in the response.

call\_id

string

The ID of the function call.

delta

string

The arguments delta as a JSON string.

OBJECT response.function\_call\_arguments.delta

```JSON
1
2
3
4
5
6
7
8
9
{
    "event_id": "event_5354",
    "type": "response.function_call_arguments.delta",
    "response_id": "resp_002",
    "item_id": "fc_001",
    "output_index": 0,
    "call_id": "call_001",
    "delta": "{\"location\": \"San\""
}
```

## response.function\_call\_arguments.done

Returned when the model-generated function call arguments are done streaming.
Also emitted when a Response is interrupted, incomplete, or cancelled.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `response.function_call_arguments.done`.

response\_id

string

The ID of the response.

item\_id

string

The ID of the function call item.

output\_index

integer

The index of the output item in the response.

call\_id

string

The ID of the function call.

arguments

string

The final arguments as a JSON string.

OBJECT response.function\_call\_arguments.done

```JSON
1
2
3
4
5
6
7
8
9
{
    "event_id": "event_5556",
    "type": "response.function_call_arguments.done",
    "response_id": "resp_002",
    "item_id": "fc_001",
    "output_index": 0,
    "call_id": "call_001",
    "arguments": "{\"location\": \"San Francisco\"}"
}
```

## rate\_limits.updated

Emitted at the beginning of a Response to indicate the updated rate limits.
When a Response is created some tokens will be "reserved" for the output
tokens, the rate limits shown here reflect that reservation, which is then
adjusted accordingly once the Response is completed.

event\_id

string

The unique ID of the server event.

type

string

The event type, must be `rate_limits.updated`.

rate\_limits

array

List of rate limit information.

Show properties

OBJECT rate\_limits.updated

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
{
    "event_id": "event_5758",
    "type": "rate_limits.updated",
    "rate_limits": [\
        {\
            "name": "requests",\
            "limit": 1000,\
            "remaining": 999,\
            "reset_seconds": 60\
        },\
        {\
            "name": "tokens",\
            "limit": 50000,\
            "remaining": 49950,\
            "reset_seconds": 60\
        }\
    ]
}
```

## Completions  Legacy

Given a prompt, the model will return one or more predicted completions along with the probabilities of alternative tokens at each position. Most developer should use our [Chat Completions API](https://platform.openai.com/docs/guides/text-generation#text-generation-models) to leverage our best and newest models.

## Create completion  Legacy

posthttps://api.openai.com/v1/completions

Creates a completion for the provided prompt and parameters.

### Request body

model

string

Required

ID of the model to use. You can use the [List models](https://platform.openai.com/docs/api-reference/models/list) API to see all of your available models, or see our [Model overview](https://platform.openai.com/docs/models) for descriptions of them.

prompt

string or array

Required

The prompt(s) to generate completions for, encoded as a string, array of strings, array of tokens, or array of token arrays.

Note that <\|endoftext\|> is the document separator that the model sees during training, so if a prompt is not specified the model will generate as if from the beginning of a new document.

best\_of

integer or null

Optional

Defaults to 1

Generates `best_of` completions server-side and returns the "best" (the one with the highest log probability per token). Results cannot be streamed.

When used with `n`, `best_of` controls the number of candidate completions and `n` specifies how many to return – `best_of` must be greater than `n`.

**Note:** Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for `max_tokens` and `stop`.

echo

boolean or null

Optional

Defaults to false

Echo back the prompt in addition to the completion

frequency\_penalty

number or null

Optional

Defaults to 0

Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.

[See more information about frequency and presence penalties.](https://platform.openai.com/docs/guides/text-generation)

logit\_bias

map

Optional

Defaults to null

Modify the likelihood of specified tokens appearing in the completion.

Accepts a JSON object that maps tokens (specified by their token ID in the GPT tokenizer) to an associated bias value from -100 to 100. You can use this [tokenizer tool](https://platform.openai.com/tokenizer?view=bpe) to convert text to token IDs. Mathematically, the bias is added to the logits generated by the model prior to sampling. The exact effect will vary per model, but values between -1 and 1 should decrease or increase likelihood of selection; values like -100 or 100 should result in a ban or exclusive selection of the relevant token.

As an example, you can pass `{"50256": -100}` to prevent the <\|endoftext\|> token from being generated.

logprobs

integer or null

Optional

Defaults to null

Include the log probabilities on the `logprobs` most likely output tokens, as well the chosen tokens. For example, if `logprobs` is 5, the API will return a list of the 5 most likely tokens. The API will always return the `logprob` of the sampled token, so there may be up to `logprobs+1` elements in the response.

The maximum value for `logprobs` is 5.

max\_tokens

integer or null

Optional

Defaults to 16

The maximum number of [tokens](https://platform.openai.com/tokenizer) that can be generated in the completion.

The token count of your prompt plus `max_tokens` cannot exceed the model's context length. [Example Python code](https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken) for counting tokens.

n

integer or null

Optional

Defaults to 1

How many completions to generate for each prompt.

**Note:** Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for `max_tokens` and `stop`.

presence\_penalty

number or null

Optional

Defaults to 0

Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.

[See more information about frequency and presence penalties.](https://platform.openai.com/docs/guides/text-generation)

seed

integer or null

Optional

If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same `seed` and parameters should return the same result.

Determinism is not guaranteed, and you should refer to the `system_fingerprint` response parameter to monitor changes in the backend.

stop

string / array / null

Optional

Defaults to null

Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.

stream

boolean or null

Optional

Defaults to false

Whether to stream back partial progress. If set, tokens will be sent as data-only [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format) as they become available, with the stream terminated by a `data: [DONE]` message. [Example Python code](https://cookbook.openai.com/examples/how_to_stream_completions).

stream\_options

object or null

Optional

Defaults to null

Options for streaming response. Only set this when you set `stream: true`.

Show properties

suffix

string or null

Optional

Defaults to null

The suffix that comes after a completion of inserted text.

This parameter is only supported for `gpt-3.5-turbo-instruct`.

temperature

number or null

Optional

Defaults to 1

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

We generally recommend altering this or `top_p` but not both.

top\_p

number or null

Optional

Defaults to 1

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or `temperature` but not both.

user

string

Optional

A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

### Returns

Returns a [completion](https://platform.openai.com/docs/api-reference/completions/object) object, or a sequence of completion objects if the request is streamed.

No streamingNo streamingStreamingStreaming

Example request

gpt-3.5-turbo-instruct

curl

```bash
1
2
3
4
5
6
7
8
9
curl https://api.openai.com/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-3.5-turbo-instruct",
    "prompt": "Say this is a test",
    "max_tokens": 7,
    "temperature": 0
  }'
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

client.completions.create(
  model="gpt-3.5-turbo-instruct",
  prompt="Say this is a test",
  max_tokens=7,
  temperature=0
)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const completion = await openai.completions.create({
    model: "gpt-3.5-turbo-instruct",
    prompt: "Say this is a test.",
    max_tokens: 7,
    temperature: 0,
  });

  console.log(completion);
}
main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "id": "cmpl-uqkvlQyYK7bGYrRHQ0eXlWi7",
  "object": "text_completion",
  "created": 1589478378,
  "model": "gpt-3.5-turbo-instruct",
  "system_fingerprint": "fp_44709d6fcb",
  "choices": [\
    {\
      "text": "\n\nThis is indeed a test",\
      "index": 0,\
      "logprobs": null,\
      "finish_reason": "length"\
    }\
  ],
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 7,
    "total_tokens": 12
  }
}
```

## The completion object  Legacy

Represents a completion response from the API. Note: both the streamed and non-streamed response objects share the same shape (unlike the chat endpoint).

id

string

A unique identifier for the completion.

choices

array

The list of completion choices the model generated for the input prompt.

Show properties

created

integer

The Unix timestamp (in seconds) of when the completion was created.

model

string

The model used for completion.

system\_fingerprint

string

This fingerprint represents the backend configuration that the model runs with.

Can be used in conjunction with the `seed` request parameter to understand when backend changes have been made that might impact determinism.

object

string

The object type, which is always "text\_completion"

usage

object

Usage statistics for the completion request.

Show properties

OBJECT The completion object

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
{
  "id": "cmpl-uqkvlQyYK7bGYrRHQ0eXlWi7",
  "object": "text_completion",
  "created": 1589478378,
  "model": "gpt-4-turbo",
  "choices": [\
    {\
      "text": "\n\nThis is indeed a test",\
      "index": 0,\
      "logprobs": null,\
      "finish_reason": "length"\
    }\
  ],
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 7,
    "total_tokens": 12
  }
}
```

## Assistants (v1)  Legacy

Build assistants that can call models and use tools to perform tasks.

[Get started with the Assistants API](https://platform.openai.com/docs/assistants)

## Create assistant (v1)  Legacy

posthttps://api.openai.com/v1/assistants

Create an assistant with a model and instructions.

### Request body

model

string

Required

ID of the model to use. You can use the [List models](https://platform.openai.com/docs/api-reference/models/list) API to see all of your available models, or see our [Model overview](https://platform.openai.com/docs/models#overview) for descriptions of them. type: string

name

string or null

Optional

The name of the assistant. The maximum length is 256 characters.

description

string or null

Optional

The description of the assistant. The maximum length is 512 characters.

instructions

string or null

Optional

The system instructions that the assistant uses. The maximum length is 256,000 characters.

tools

array

Optional

Defaults to \[\]

A list of tool enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can be of types `code_interpreter`, `retrieval`, or `function`.

Show possible types

file\_ids

array

Optional

Defaults to \[\]

A list of [file](https://platform.openai.com/docs/api-reference/files) IDs attached to this assistant. There can be a maximum of 20 files attached to the assistant. Files are ordered by their creation date in ascending order.

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

temperature

number or null

Optional

Defaults to 1

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

top\_p

number or null

Optional

Defaults to 1

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

response\_format

string or object

Optional

Specifies the format that the model must output. Compatible with [GPT-4o](https://platform.openai.com/docs/models#gpt-4o), [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4), and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

Show possible types

### Returns

An [assistant](https://platform.openai.com/docs/api-reference/assistants-v1/object) object.

Code InterpreterCode InterpreterFilesFiles

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
10
curl "https://api.openai.com/v1/assistants" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1" \
  -d '{
    "instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
    "name": "Math Tutor",
    "tools": [{"type": "code_interpreter"}],
    "model": "gpt-4-turbo"
  }'
```

```python
1
2
3
4
5
6
7
8
9
10
from openai import OpenAI
client = OpenAI()

my_assistant = client.beta.assistants.create(
    instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
    name="Math Tutor",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-turbo",
)
print(my_assistant)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const myAssistant = await openai.beta.assistants.create({
    instructions:
      "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
    name: "Math Tutor",
    tools: [{ type: "code_interpreter" }],
    model: "gpt-4-turbo",
  });

  console.log(myAssistant);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
{
  "id": "asst_abc123",
  "object": "assistant",
  "created_at": 1698984975,
  "name": "Math Tutor",
  "description": null,
  "model": "gpt-4-turbo",
  "instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
  "tools": [\
    {\
      "type": "code_interpreter"\
    }\
  ],
  "file_ids": [],
  "metadata": {},
  "top_p": 1.0,
  "temperature": 1.0,
  "response_format": "auto"
}
```

## Create assistant file (v1)  Legacy

posthttps://api.openai.com/v1/assistants/{assistant\_id}/files

Create an assistant file by attaching a [File](https://platform.openai.com/docs/api-reference/files) to an [assistant](https://platform.openai.com/docs/api-reference/assistants-v1).

### Path parameters

assistant\_id

string

Required

The ID of the assistant for which to create a File.

### Request body

file\_id

string

Required

A [File](https://platform.openai.com/docs/api-reference/files) ID (with `purpose="assistants"`) that the assistant should use. Useful for tools like `retrieval` and `code_interpreter` that can access files.

### Returns

An [assistant file](https://platform.openai.com/docs/api-reference/assistants-v1/file-object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
curl https://api.openai.com/v1/assistants/asst_abc123/files \
    -H 'Authorization: Bearer $OPENAI_API_KEY"' \
    -H 'Content-Type: application/json' \
    -H 'OpenAI-Beta: assistants=v1' \
    -d '{
      "file_id": "file-abc123"
    }'
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

assistant_file = client.beta.assistants.files.create(
  assistant_id="asst_abc123",
  file_id="file-abc123"
)
print(assistant_file)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const myAssistantFile = await openai.beta.assistants.files.create(
    "asst_abc123",
    {
      file_id: "file-abc123"
    }
  );
  console.log(myAssistantFile);
}

main();
```

Response

```json
1
2
3
4
5
6
{
  "id": "file-abc123",
  "object": "assistant.file",
  "created_at": 1699055364,
  "assistant_id": "asst_abc123"
}
```

## List assistants (v1)  Legacy

gethttps://api.openai.com/v1/assistants

Returns a list of assistants.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

### Returns

A list of [assistant](https://platform.openai.com/docs/api-reference/assistants-v1/object) objects.

Example request

curl

```bash
1
2
3
4
curl "https://api.openai.com/v1/assistants?order=desc&limit=20" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

my_assistants = client.beta.assistants.list(
    order="desc",
    limit="20",
)
print(my_assistants.data)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const myAssistants = await openai.beta.assistants.list({
    order: "desc",
    limit: "20",
  });

  console.log(myAssistants.data);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
{
  "object": "list",
  "data": [\
    {\
      "id": "asst_abc123",\
      "object": "assistant",\
      "created_at": 1698982736,\
      "name": "Coding Tutor",\
      "description": null,\
      "model": "gpt-4-turbo",\
      "instructions": "You are a helpful assistant designed to make me better at coding!",\
      "tools": [],\
      "file_ids": [],\
      "metadata": {},\
      "top_p": 1.0,\
      "temperature": 1.0,\
      "response_format": "auto"\
    },\
    {\
      "id": "asst_abc456",\
      "object": "assistant",\
      "created_at": 1698982718,\
      "name": "My Assistant",\
      "description": null,\
      "model": "gpt-4-turbo",\
      "instructions": "You are a helpful assistant designed to make me better at coding!",\
      "tools": [],\
      "file_ids": [],\
      "metadata": {},\
      "top_p": 1.0,\
      "temperature": 1.0,\
      "response_format": "auto"\
    },\
    {\
      "id": "asst_abc789",\
      "object": "assistant",\
      "created_at": 1698982643,\
      "name": null,\
      "description": null,\
      "model": "gpt-4-turbo",\
      "instructions": null,\
      "tools": [],\
      "file_ids": [],\
      "metadata": {},\
      "top_p": 1.0,\
      "temperature": 1.0,\
      "response_format": "auto"\
    }\
  ],
  "first_id": "asst_abc123",
  "last_id": "asst_abc789",
  "has_more": false
}
```

## List assistant files (v1)  Legacy

gethttps://api.openai.com/v1/assistants/{assistant\_id}/files

Returns a list of assistant files.

### Path parameters

assistant\_id

string

Required

The ID of the assistant the file belongs to.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

### Returns

A list of [assistant file](https://platform.openai.com/docs/api-reference/assistants-v1/file-object) objects.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/assistants/asst_abc123/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1"
```

```python
1
2
3
4
5
6
7
from openai import OpenAI
client = OpenAI()

assistant_files = client.beta.assistants.files.list(
  assistant_id="asst_abc123"
)
print(assistant_files)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const assistantFiles = await openai.beta.assistants.files.list(
    "asst_abc123"
  );
  console.log(assistantFiles);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "object": "list",
  "data": [\
    {\
      "id": "file-abc123",\
      "object": "assistant.file",\
      "created_at": 1699060412,\
      "assistant_id": "asst_abc123"\
    },\
    {\
      "id": "file-abc456",\
      "object": "assistant.file",\
      "created_at": 1699060412,\
      "assistant_id": "asst_abc123"\
    }\
  ],
  "first_id": "file-abc123",
  "last_id": "file-abc456",
  "has_more": false
}
```

## Retrieve assistant (v1)  Legacy

gethttps://api.openai.com/v1/assistants/{assistant\_id}

Retrieves an assistant.

### Path parameters

assistant\_id

string

Required

The ID of the assistant to retrieve.

### Returns

The [assistant](https://platform.openai.com/docs/api-reference/assistants-v1/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/assistants/asst_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1"
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

my_assistant = client.beta.assistants.retrieve("asst_abc123")
print(my_assistant)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const myAssistant = await openai.beta.assistants.retrieve(
    "asst_abc123"
  );

  console.log(myAssistant);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
{
  "id": "asst_abc123",
  "object": "assistant",
  "created_at": 1699009709,
  "name": "HR Helper",
  "description": null,
  "model": "gpt-4-turbo",
  "instructions": "You are an HR bot, and you have access to files to answer employee questions about company policies.",
  "tools": [\
    {\
      "type": "retrieval"\
    }\
  ],
  "file_ids": [\
    "file-abc123"\
  ],
  "metadata": {}
}
```

## Retrieve assistant file (v1)  Legacy

gethttps://api.openai.com/v1/assistants/{assistant\_id}/files/{file\_id}

Retrieves an AssistantFile.

### Path parameters

assistant\_id

string

Required

The ID of the assistant who the file belongs to.

file\_id

string

Required

The ID of the file we're getting.

### Returns

The [assistant file](https://platform.openai.com/docs/api-reference/assistants-v1/file-object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/assistants/asst_abc123/files/file-abc123 \
  -H 'Authorization: Bearer $OPENAI_API_KEY"' \
  -H 'Content-Type: application/json' \
  -H 'OpenAI-Beta: assistants=v1'
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

assistant_file = client.beta.assistants.files.retrieve(
  assistant_id="asst_abc123",
  file_id="file-abc123"
)
print(assistant_file)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const myAssistantFile = await openai.beta.assistants.files.retrieve(
    "asst_abc123",
    "file-abc123"
  );
  console.log(myAssistantFile);
}

main();
```

Response

```json
1
2
3
4
5
6
{
  "id": "file-abc123",
  "object": "assistant.file",
  "created_at": 1699055364,
  "assistant_id": "asst_abc123"
}
```

## Modify assistant (v1)  Legacy

posthttps://api.openai.com/v1/assistants/{assistant\_id}

Modifies an assistant.

### Path parameters

assistant\_id

string

Required

The ID of the assistant to modify.

### Request body

model

Optional

ID of the model to use. You can use the [List models](https://platform.openai.com/docs/api-reference/models/list) API to see all of your available models, or see our [Model overview](https://platform.openai.com/docs/models#overview) for descriptions of them. type: string

name

string or null

Optional

The name of the assistant. The maximum length is 256 characters.

description

string or null

Optional

The description of the assistant. The maximum length is 512 characters.

instructions

string or null

Optional

The system instructions that the assistant uses. The maximum length is 256,000 characters.

tools

array

Optional

Defaults to \[\]

A list of tool enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can be of types `code_interpreter`, `retrieval`, or `function`.

Show possible types

file\_ids

array

Optional

Defaults to \[\]

A list of [File](https://platform.openai.com/docs/api-reference/files) IDs attached to this assistant. There can be a maximum of 20 files attached to the assistant. Files are ordered by their creation date in ascending order. If a file was previously attached to the list but does not show up in the list, it will be deleted from the assistant.

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

temperature

number or null

Optional

Defaults to 1

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

top\_p

number or null

Optional

Defaults to 1

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

response\_format

string or object

Optional

Specifies the format that the model must output. Compatible with [GPT-4o](https://platform.openai.com/docs/models#gpt-4o), [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4), and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

Show possible types

### Returns

The modified [assistant](https://platform.openai.com/docs/api-reference/assistants-v1/object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
10
curl https://api.openai.com/v1/assistants/asst_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1" \
  -d '{
      "instructions": "You are an HR bot, and you have access to files to answer employee questions about company policies. Always response with info from either of the files.",
      "tools": [{"type": "retrieval"}],
      "model": "gpt-4-turbo",
      "file_ids": ["file-abc123", "file-abc456"]
    }'
```

```python
1
2
3
4
5
6
7
8
9
10
11
12
13
from openai import OpenAI
client = OpenAI()

my_updated_assistant = client.beta.assistants.update(
  "asst_abc123",
  instructions="You are an HR bot, and you have access to files to answer employee questions about company policies. Always response with info from either of the files.",
  name="HR Helper",
  tools=[{"type": "retrieval"}],
  model="gpt-4-turbo",
  file_ids=["file-abc123", "file-abc456"],
)

print(my_updated_assistant)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const myUpdatedAssistant = await openai.beta.assistants.update(
    "asst_abc123",
    {
      instructions:
        "You are an HR bot, and you have access to files to answer employee questions about company policies. Always response with info from either of the files.",
      name: "HR Helper",
      tools: [{ type: "retrieval" }],
      model: "gpt-4-turbo",
      file_ids: [\
        "file-abc123",\
        "file-abc456",\
      ],
    }
  );

  console.log(myUpdatedAssistant);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
{
  "id": "asst_abc123",
  "object": "assistant",
  "created_at": 1699009709,
  "name": "HR Helper",
  "description": null,
  "model": "gpt-4-turbo",
  "instructions": "You are an HR bot, and you have access to files to answer employee questions about company policies. Always response with info from either of the files.",
  "tools": [\
    {\
      "type": "retrieval"\
    }\
  ],
  "file_ids": [\
    "file-abc123",\
    "file-abc456"\
  ],
  "metadata": {},
  "top_p": 1.0,
  "temperature": 1.0,
  "response_format": "auto"
}
```

## Delete assistant (v1)  Legacy

deletehttps://api.openai.com/v1/assistants/{assistant\_id}

Delete an assistant.

### Path parameters

assistant\_id

string

Required

The ID of the assistant to delete.

### Returns

Deletion status

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/assistants/asst_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1" \
  -X DELETE
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

response = client.beta.assistants.delete("asst_abc123")
print(response)
```

```javascript
1
2
3
4
5
6
7
8
9
10
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const response = await openai.beta.assistants.del("asst_abc123");

  console.log(response);
}
main();
```

Response

```json
1
2
3
4
5
{
  "id": "asst_abc123",
  "object": "assistant.deleted",
  "deleted": true
}
```

## Delete assistant file (v1)  Legacy

deletehttps://api.openai.com/v1/assistants/{assistant\_id}/files/{file\_id}

Delete an assistant file.

### Path parameters

assistant\_id

string

Required

The ID of the assistant that the file belongs to.

file\_id

string

Required

The ID of the file to delete.

### Returns

Deletion status

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/assistants/asst_abc123/files/file-abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1" \
  -X DELETE
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

deleted_assistant_file = client.beta.assistants.files.delete(
    assistant_id="asst_abc123",
    file_id="file-abc123"
)
print(deleted_assistant_file)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const deletedAssistantFile = await openai.beta.assistants.files.del(
    "asst_abc123",
    "file-abc123"
  );
  console.log(deletedAssistantFile);
}

main();
```

Response

```json
1
2
3
4
5
{
  id: "file-abc123",
  object: "assistant.file.deleted",
  deleted: true
}
```

## The assistant object (v1)  Legacy

Represents an `assistant` that can call the model and use tools.

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `assistant`.

created\_at

integer

The Unix timestamp (in seconds) for when the assistant was created.

name

string or null

The name of the assistant. The maximum length is 256 characters.

description

string or null

The description of the assistant. The maximum length is 512 characters.

model

ID of the model to use. You can use the [List models](https://platform.openai.com/docs/api-reference/models/list) API to see all of your available models, or see our [Model overview](https://platform.openai.com/docs/models#overview) for descriptions of them. type: string

instructions

string or null

The system instructions that the assistant uses. The maximum length is 256,000 characters.

tools

array

A list of tool enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can be of types `code_interpreter`, `retrieval`, or `function`.

Show possible types

file\_ids

array

A list of [file](https://platform.openai.com/docs/api-reference/files) IDs attached to this assistant. There can be a maximum of 20 files attached to the assistant. Files are ordered by their creation date in ascending order.

metadata

map

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

temperature

number or null

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

top\_p

number or null

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

response\_format

string or object

Specifies the format that the model must output. Compatible with [GPT-4o](https://platform.openai.com/docs/models#gpt-4o), [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4), and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

Show possible types

OBJECT The assistant object (v1)

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
{
  "id": "asst_abc123",
  "object": "assistant",
  "created_at": 1698984975,
  "name": "Math Tutor",
  "description": null,
  "model": "gpt-4-turbo",
  "instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
  "tools": [\
    {\
      "type": "code_interpreter"\
    }\
  ],
  "file_ids": [],
  "metadata": {},
  "top_p": 1.0,
  "temperature": 1.0,
  "response_format": "auto"
}
```

## The assistant file object (v1)  Legacy

A list of [Files](https://platform.openai.com/docs/api-reference/files) attached to an `assistant`.

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `assistant.file`.

created\_at

integer

The Unix timestamp (in seconds) for when the assistant file was created.

assistant\_id

string

The assistant ID that the file is attached to.

OBJECT The assistant file object (v1)

```JSON
1
2
3
4
5
6
{
  "id": "file-abc123",
  "object": "assistant.file",
  "created_at": 1699055364,
  "assistant_id": "asst_abc123"
}
```

## Threads (v1)  Legacy

Create threads that assistants can interact with.

Related guide: [Assistants](https://platform.openai.com/docs/assistants/overview)

## Create thread (v1)  Legacy

posthttps://api.openai.com/v1/threads

Create a thread.

### Request body

messages

array

Optional

A list of [messages](https://platform.openai.com/docs/api-reference/messages-v1) to start the thread with.

Show properties

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

### Returns

A [thread](https://platform.openai.com/docs/api-reference/threads-v1) object.

EmptyEmptyMessagesMessages

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/threads \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1" \
  -d ''
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

empty_thread = client.beta.threads.create()
print(empty_thread)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const emptyThread = await openai.beta.threads.create();

  console.log(emptyThread);
}

main();
```

Response

```json
1
2
3
4
5
6
{
  "id": "thread_abc123",
  "object": "thread",
  "created_at": 1699012949,
  "metadata": {}
}
```

## Retrieve thread (v1)  Legacy

gethttps://api.openai.com/v1/threads/{thread\_id}

Retrieves a thread.

### Path parameters

thread\_id

string

Required

The ID of the thread to retrieve.

### Returns

The [thread](https://platform.openai.com/docs/api-reference/threads-v1/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1"
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

my_thread = client.beta.threads.retrieve("thread_abc123")
print(my_thread)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const myThread = await openai.beta.threads.retrieve(
    "thread_abc123"
  );

  console.log(myThread);
}

main();
```

Response

```json
1
2
3
4
5
6
{
  "id": "thread_abc123",
  "object": "thread",
  "created_at": 1699014083,
  "metadata": {}
}
```

## Modify thread (v1)  Legacy

posthttps://api.openai.com/v1/threads/{thread\_id}

Modifies a thread.

### Path parameters

thread\_id

string

Required

The ID of the thread to modify. Only the `metadata` can be modified.

### Request body

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

### Returns

The modified [thread](https://platform.openai.com/docs/api-reference/threads-v1/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
10
curl https://api.openai.com/v1/threads/thread_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1" \
  -d '{
      "metadata": {
        "modified": "true",
        "user": "abc123"
      }
    }'
```

```python
1
2
3
4
5
6
7
8
9
10
11
from openai import OpenAI
client = OpenAI()

my_updated_thread = client.beta.threads.update(
  "thread_abc123",
  metadata={
    "modified": "true",
    "user": "abc123"
  }
)
print(my_updated_thread)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const updatedThread = await openai.beta.threads.update(
    "thread_abc123",
    {
      metadata: { modified: "true", user: "abc123" },
    }
  );

  console.log(updatedThread);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
{
  "id": "thread_abc123",
  "object": "thread",
  "created_at": 1699014083,
  "metadata": {
    "modified": "true",
    "user": "abc123"
  }
}
```

## Delete thread (v1)  Legacy

deletehttps://api.openai.com/v1/threads/{thread\_id}

Delete a thread.

### Path parameters

thread\_id

string

Required

The ID of the thread to delete.

### Returns

Deletion status

Example request

curl

```bash
1
2
3
4
5
curl https://api.openai.com/v1/threads/thread_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1" \
  -X DELETE
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

response = client.beta.threads.delete("thread_abc123")
print(response)
```

```javascript
1
2
3
4
5
6
7
8
9
10
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const response = await openai.beta.threads.del("thread_abc123");

  console.log(response);
}
main();
```

Response

```json
1
2
3
4
5
{
  "id": "thread_abc123",
  "object": "thread.deleted",
  "deleted": true
}
```

## The thread object (v1)  Legacy

Represents a thread that contains [messages](https://platform.openai.com/docs/api-reference/messages-v1).

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `thread`.

created\_at

integer

The Unix timestamp (in seconds) for when the thread was created.

metadata

map

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

OBJECT The thread object (v1)

```JSON
1
2
3
4
5
6
{
  "id": "thread_abc123",
  "object": "thread",
  "created_at": 1698107661,
  "metadata": {}
}
```

## Messages (v1)  Legacy

Create messages within threads

Related guide: [Assistants](https://platform.openai.com/docs/assistants/overview)

## Create message (v1)  Legacy

posthttps://api.openai.com/v1/threads/{thread\_id}/messages

Create a message.

### Path parameters

thread\_id

string

Required

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads-v1) to create a message for.

### Request body

role

string

Required

The role of the entity that is creating the message. Allowed values include:

- `user`: Indicates the message is sent by an actual user and should be used in most cases to represent user-generated messages.
- `assistant`: Indicates the message is generated by the assistant. Use this value to insert messages from the assistant into the conversation.

content

string

Required

The content of the message.

file\_ids

array

Optional

Defaults to \[\]

A list of [File](https://platform.openai.com/docs/api-reference/files) IDs that the message should use. There can be a maximum of 10 files attached to a message. Useful for tools like `retrieval` and `code_interpreter` that can access and use files.

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

### Returns

A [message](https://platform.openai.com/docs/api-reference/messages-v1/object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
8
curl https://api.openai.com/v1/threads/thread_abc123/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1" \
  -d '{
      "role": "user",
      "content": "How does AI work? Explain it in simple terms."
    }'
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

thread_message = client.beta.threads.messages.create(
  "thread_abc123",
  role="user",
  content="How does AI work? Explain it in simple terms.",
)
print(thread_message)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const threadMessages = await openai.beta.threads.messages.create(
    "thread_abc123",
    { role: "user", content: "How does AI work? Explain it in simple terms." }
  );

  console.log(threadMessages);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "id": "msg_abc123",
  "object": "thread.message",
  "created_at": 1699017614,
  "thread_id": "thread_abc123",
  "role": "user",
  "content": [\
    {\
      "type": "text",\
      "text": {\
        "value": "How does AI work? Explain it in simple terms.",\
        "annotations": []\
      }\
    }\
  ],
  "file_ids": [],
  "assistant_id": null,
  "run_id": null,
  "metadata": {}
}
```

## List messages (v1)  Legacy

gethttps://api.openai.com/v1/threads/{thread\_id}/messages

Returns a list of messages for a given thread.

### Path parameters

thread\_id

string

Required

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads-v1) the messages belong to.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

run\_id

string

Optional

Filter messages by the run ID that generated them.

### Returns

A list of [message](https://platform.openai.com/docs/api-reference/messages-v1) objects.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1"
```

```python
1
2
3
4
5
from openai import OpenAI
client = OpenAI()

thread_messages = client.beta.threads.messages.list("thread_abc123")
print(thread_messages.data)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const threadMessages = await openai.beta.threads.messages.list(
    "thread_abc123"
  );

  console.log(threadMessages.data);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
{
  "object": "list",
  "data": [\
    {\
      "id": "msg_abc123",\
      "object": "thread.message",\
      "created_at": 1699016383,\
      "thread_id": "thread_abc123",\
      "role": "user",\
      "content": [\
        {\
          "type": "text",\
          "text": {\
            "value": "How does AI work? Explain it in simple terms.",\
            "annotations": []\
          }\
        }\
      ],\
      "file_ids": [],\
      "assistant_id": null,\
      "run_id": null,\
      "metadata": {}\
    },\
    {\
      "id": "msg_abc456",\
      "object": "thread.message",\
      "created_at": 1699016383,\
      "thread_id": "thread_abc123",\
      "role": "user",\
      "content": [\
        {\
          "type": "text",\
          "text": {\
            "value": "Hello, what is AI?",\
            "annotations": []\
          }\
        }\
      ],\
      "file_ids": [\
        "file-abc123"\
      ],\
      "assistant_id": null,\
      "run_id": null,\
      "metadata": {}\
    }\
  ],
  "first_id": "msg_abc123",
  "last_id": "msg_abc456",
  "has_more": false
}
```

## List message files (v1)  Legacy

gethttps://api.openai.com/v1/threads/{thread\_id}/messages/{message\_id}/files

Returns a list of message files.

### Path parameters

thread\_id

string

Required

The ID of the thread that the message and files belong to.

message\_id

string

Required

The ID of the message that the files belongs to.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

### Returns

A list of [message file](https://platform.openai.com/docs/api-reference/messages-v1/file-object) objects.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/messages/msg_abc123/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

message_files = client.beta.threads.messages.files.list(
  thread_id="thread_abc123",
  message_id="msg_abc123"
)
print(message_files)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const messageFiles = await openai.beta.threads.messages.files.list(
    "thread_abc123",
    "msg_abc123"
  );
  console.log(messageFiles);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "object": "list",
  "data": [\
    {\
      "id": "file-abc123",\
      "object": "thread.message.file",\
      "created_at": 1699061776,\
      "message_id": "msg_abc123"\
    },\
    {\
      "id": "file-abc123",\
      "object": "thread.message.file",\
      "created_at": 1699061776,\
      "message_id": "msg_abc123"\
    }\
  ],
  "first_id": "file-abc123",
  "last_id": "file-abc123",
  "has_more": false
}
```

## Retrieve message (v1)  Legacy

gethttps://api.openai.com/v1/threads/{thread\_id}/messages/{message\_id}

Retrieve a message.

### Path parameters

thread\_id

string

Required

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads-v1) to which this message belongs.

message\_id

string

Required

The ID of the message to retrieve.

### Returns

The [message](https://platform.openai.com/docs/api-reference/threads-v1/messages/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/messages/msg_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

message = client.beta.threads.messages.retrieve(
  message_id="msg_abc123",
  thread_id="thread_abc123",
)
print(message)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const message = await openai.beta.threads.messages.retrieve(
    "thread_abc123",
    "msg_abc123"
  );

  console.log(message);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "id": "msg_abc123",
  "object": "thread.message",
  "created_at": 1699017614,
  "thread_id": "thread_abc123",
  "role": "user",
  "content": [\
    {\
      "type": "text",\
      "text": {\
        "value": "How does AI work? Explain it in simple terms.",\
        "annotations": []\
      }\
    }\
  ],
  "file_ids": [],
  "assistant_id": null,
  "run_id": null,
  "metadata": {}
}
```

## Retrieve message file (v1)  Legacy

gethttps://api.openai.com/v1/threads/{thread\_id}/messages/{message\_id}/files/{file\_id}

Retrieves a message file.

### Path parameters

thread\_id

string

Required

The ID of the thread to which the message and File belong.

message\_id

string

Required

The ID of the message the file belongs to.

file\_id

string

Required

The ID of the file being retrieved.

### Returns

The [message file](https://platform.openai.com/docs/api-reference/messages-v1/file-object) object.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/messages/msg_abc123/files/file-abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1"
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

message_files = client.beta.threads.messages.files.retrieve(
    thread_id="thread_abc123",
    message_id="msg_abc123",
    file_id="file-abc123"
)
print(message_files)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const messageFile = await openai.beta.threads.messages.files.retrieve(
    "thread_abc123",
    "msg_abc123",
    "file-abc123"
  );
  console.log(messageFile);
}

main();
```

Response

```json
1
2
3
4
5
6
{
  "id": "file-abc123",
  "object": "thread.message.file",
  "created_at": 1699061776,
  "message_id": "msg_abc123"
}
```

## Modify message (v1)  Legacy

posthttps://api.openai.com/v1/threads/{thread\_id}/messages/{message\_id}

Modifies a message.

### Path parameters

thread\_id

string

Required

The ID of the thread to which this message belongs.

message\_id

string

Required

The ID of the message to modify.

### Request body

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

### Returns

The modified [message](https://platform.openai.com/docs/api-reference/threads-v1/messages/object) object.

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
10
curl https://api.openai.com/v1/threads/thread_abc123/messages/msg_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1" \
  -d '{
      "metadata": {
        "modified": "true",
        "user": "abc123"
      }
    }'
```

```python
1
2
3
4
5
6
7
8
9
10
11
12
from openai import OpenAI
client = OpenAI()

message = client.beta.threads.messages.update(
  message_id="msg_abc12",
  thread_id="thread_abc123",
  metadata={
    "modified": "true",
    "user": "abc123",
  },
)
print(message)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const message = await openai.beta.threads.messages.update(
    "thread_abc123",
    "msg_abc123",
    {
      metadata: {
        modified: "true",
        user: "abc123",
      },
    }
  }'
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
{
  "id": "msg_abc123",
  "object": "thread.message",
  "created_at": 1699017614,
  "thread_id": "thread_abc123",
  "role": "user",
  "content": [\
    {\
      "type": "text",\
      "text": {\
        "value": "How does AI work? Explain it in simple terms.",\
        "annotations": []\
      }\
    }\
  ],
  "file_ids": [],
  "assistant_id": null,
  "run_id": null,
  "metadata": {
    "modified": "true",
    "user": "abc123"
  }
}
```

## The message object (v1)  Legacy

Represents a message within a [thread](https://platform.openai.com/docs/api-reference/threads-v1).

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `thread.message`.

created\_at

integer

The Unix timestamp (in seconds) for when the message was created.

thread\_id

string

The [thread](https://platform.openai.com/docs/api-reference/threads-v1) ID that this message belongs to.

status

string

The status of the message, which can be either `in_progress`, `incomplete`, or `completed`.

incomplete\_details

object or null

On an incomplete message, details about why the message is incomplete.

Show properties

completed\_at

integer or null

The Unix timestamp (in seconds) for when the message was completed.

incomplete\_at

integer or null

The Unix timestamp (in seconds) for when the message was marked as incomplete.

role

string

The entity that produced the message. One of `user` or `assistant`.

content

array

The content of the message in array of text and/or images.

Show possible types

assistant\_id

string or null

If applicable, the ID of the [assistant](https://platform.openai.com/docs/api-reference/assistants-v1) that authored this message.

run\_id

string or null

The ID of the [run](https://platform.openai.com/docs/api-reference/runs-v1) associated with the creation of this message. Value is `null` when messages are created manually using the create message or create thread endpoints.

file\_ids

array

A list of [file](https://platform.openai.com/docs/api-reference/files) IDs that the assistant should use. Useful for tools like retrieval and code\_interpreter that can access files. A maximum of 10 files can be attached to a message.

metadata

map

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

OBJECT The message object (v1)

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
{
  "id": "msg_abc123",
  "object": "thread.message",
  "created_at": 1698983503,
  "thread_id": "thread_abc123",
  "role": "assistant",
  "content": [\
    {\
      "type": "text",\
      "text": {\
        "value": "Hi! How can I help you today?",\
        "annotations": []\
      }\
    }\
  ],
  "file_ids": [],
  "assistant_id": "asst_abc123",
  "run_id": "run_abc123",
  "metadata": {}
}
```

## The message file object (v1)  Legacy

A list of files attached to a `message`.

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `thread.message.file`.

created\_at

integer

The Unix timestamp (in seconds) for when the message file was created.

message\_id

string

The ID of the [message](https://platform.openai.com/docs/api-reference/messages-v1) that the [File](https://platform.openai.com/docs/api-reference/files) is attached to.

OBJECT The message file object (v1)

```JSON
1
2
3
4
5
6
7
{
  "id": "file-abc123",
  "object": "thread.message.file",
  "created_at": 1698107661,
  "message_id": "message_QLoItBbqwyAJEzlTy4y9kOMM",
  "file_id": "file-abc123"
}
```

## Runs (v1)  Legacy

Represents an execution run on a thread.

Related guide: [Assistants](https://platform.openai.com/docs/assistants/overview)

## Create run (v1)  Legacy

posthttps://api.openai.com/v1/threads/{thread\_id}/runs

Create a run.

### Path parameters

thread\_id

string

Required

The ID of the thread to run.

### Request body

assistant\_id

string

Required

The ID of the [assistant](https://platform.openai.com/docs/api-reference/assistants-v1) to use to execute this run.

model

string

Optional

The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to be used to execute this run. If a value is provided here, it will override the model associated with the assistant. If not, the model associated with the assistant will be used.

instructions

string or null

Optional

Overrides the [instructions](https://platform.openai.com/docs/api-reference/assistants-v1/createAssistant) of the assistant. This is useful for modifying the behavior on a per-run basis.

additional\_instructions

string or null

Optional

Appends additional instructions at the end of the instructions for the run. This is useful for modifying the behavior on a per-run basis without overriding other instructions.

additional\_messages

array or null

Optional

Adds additional messages to the thread before creating the run.

Show properties

tools

array or null

Optional

Override the tools the assistant can use for this run. This is useful for modifying the behavior on a per-run basis.

Show possible types

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

temperature

number or null

Optional

Defaults to 1

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

top\_p

number or null

Optional

Defaults to 1

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

stream

boolean or null

Optional

If `true`, returns a stream of events that happen during the Run as server-sent events, terminating when the Run enters a terminal state with a `data: [DONE]` message.

max\_prompt\_tokens

integer or null

Optional

The maximum number of prompt tokens that may be used over the course of the run. The run will make a best effort to use only the number of prompt tokens specified, across multiple turns of the run. If the run exceeds the number of prompt tokens specified, the run will end with status `complete`. See `incomplete_details` for more info.

max\_completion\_tokens

integer or null

Optional

The maximum number of completion tokens that may be used over the course of the run. The run will make a best effort to use only the number of completion tokens specified, across multiple turns of the run. If the run exceeds the number of completion tokens specified, the run will end with status `complete`. See `incomplete_details` for more info.

truncation\_strategy

object

Optional

Show properties

tool\_choice

string or object

Optional

Controls which (if any) tool is called by the model.
`none` means the model will not call any tools and instead generates a message.
`auto` is the default value and means the model can pick between generating a message or calling a tool.
Specifying a particular tool like `{"type": "TOOL_TYPE"}` or `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool.

Show possible types

response\_format

string or object

Optional

Specifies the format that the model must output. Compatible with [GPT-4o](https://platform.openai.com/docs/models#gpt-4o), [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4), and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

Show possible types

### Returns

A [run](https://platform.openai.com/docs/api-reference/runs-v1/object) object.

DefaultDefaultStreamingStreamingStreaming with FunctionsStreaming with Functions

Example request

curl

```bash
1
2
3
4
5
6
7
curl https://api.openai.com/v1/threads/thread_abc123/runs \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1" \
  -d '{
    "assistant_id": "asst_abc123"
  }'
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

run = client.beta.threads.runs.create(
  thread_id="thread_abc123",
  assistant_id="asst_abc123"
)

print(run)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const run = await openai.beta.threads.runs.create(
    "thread_abc123",
    { assistant_id: "asst_abc123" }
  );

  console.log(run);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
{
  "id": "run_abc123",
  "object": "thread.run",
  "created_at": 1699063290,
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "status": "queued",
  "started_at": 1699063290,
  "expires_at": null,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": 1699063291,
  "last_error": null,
  "model": "gpt-4-turbo",
  "instructions": null,
  "incomplete_details": null,
  "tools": [\
    {\
      "type": "code_interpreter"\
    }\
  ],
  "file_ids": [\
    "file-abc123",\
    "file-abc456"\
  ],
  "metadata": {},
  "usage": null,
  "temperature": 1.0,
  "top_p": 1.0,
  "max_prompt_tokens": 1000,
  "max_completion_tokens": 1000,
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "response_format": "auto",
  "tool_choice": "auto"
}
```

## Create thread and run (v1)  Legacy

posthttps://api.openai.com/v1/threads/runs

Create a thread and run it in one request.

### Request body

assistant\_id

string

Required

The ID of the [assistant](https://platform.openai.com/docs/api-reference/assistants-v1) to use to execute this run.

thread

object

Optional

Show properties

model

string

Optional

The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to be used to execute this run. If a value is provided here, it will override the model associated with the assistant. If not, the model associated with the assistant will be used.

instructions

string or null

Optional

Override the default system message of the assistant. This is useful for modifying the behavior on a per-run basis.

tools

array or null

Optional

Override the tools the assistant can use for this run. This is useful for modifying the behavior on a per-run basis.

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

temperature

number or null

Optional

Defaults to 1

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

top\_p

number or null

Optional

Defaults to 1

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

stream

boolean or null

Optional

If `true`, returns a stream of events that happen during the Run as server-sent events, terminating when the Run enters a terminal state with a `data: [DONE]` message.

max\_prompt\_tokens

integer or null

Optional

The maximum number of prompt tokens that may be used over the course of the run. The run will make a best effort to use only the number of prompt tokens specified, across multiple turns of the run. If the run exceeds the number of prompt tokens specified, the run will end with status `complete`. See `incomplete_details` for more info.

max\_completion\_tokens

integer or null

Optional

The maximum number of completion tokens that may be used over the course of the run. The run will make a best effort to use only the number of completion tokens specified, across multiple turns of the run. If the run exceeds the number of completion tokens specified, the run will end with status `complete`. See `incomplete_details` for more info.

truncation\_strategy

object

Optional

Show properties

tool\_choice

string or object

Optional

Controls which (if any) tool is called by the model.
`none` means the model will not call any tools and instead generates a message.
`auto` is the default value and means the model can pick between generating a message or calling a tool.
Specifying a particular tool like `{"type": "TOOL_TYPE"}` or `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool.

Show possible types

response\_format

string or object

Optional

Specifies the format that the model must output. Compatible with [GPT-4o](https://platform.openai.com/docs/models#gpt-4o), [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4), and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

Show possible types

### Returns

A [run](https://platform.openai.com/docs/api-reference/runs-v1/object) object.

DefaultDefaultStreamingStreamingStreaming with FunctionsStreaming with Functions

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
10
11
12
curl https://api.openai.com/v1/threads/runs \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1" \
  -d '{
      "assistant_id": "asst_abc123",
      "thread": {
        "messages": [\
          {"role": "user", "content": "Explain deep learning to a 5 year old."}\
        ]
      }
    }'
```

```python
1
2
3
4
5
6
7
8
9
10
11
12
13
from openai import OpenAI
client = OpenAI()

run = client.beta.threads.create_and_run(
  assistant_id="asst_abc123",
  thread={
    "messages": [\
      {"role": "user", "content": "Explain deep learning to a 5 year old."}\
    ]
  }
)

print(run)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const run = await openai.beta.threads.createAndRun({
    assistant_id: "asst_abc123",
    thread: {
      messages: [\
        { role: "user", content: "Explain deep learning to a 5 year old." },\
      ],
    },
  });

  console.log(run);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
{
  "id": "run_abc123",
  "object": "thread.run",
  "created_at": 1699076792,
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "status": "queued",
  "started_at": null,
  "expires_at": 1699077392,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": null,
  "last_error": null,
  "model": "gpt-4-turbo",
  "instructions": "You are a helpful assistant.",
  "tools": [],
  "file_ids": [],
  "metadata": {},
  "usage": null,
  "temperature": 1
}
```

## List runs (v1)  Legacy

gethttps://api.openai.com/v1/threads/{thread\_id}/runs

Returns a list of runs belonging to a thread.

### Path parameters

thread\_id

string

Required

The ID of the thread the run belongs to.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

### Returns

A list of [run](https://platform.openai.com/docs/api-reference/runs-v1/object) objects.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/runs \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1"
```

```python
1
2
3
4
5
6
7
8
from openai import OpenAI
client = OpenAI()

runs = client.beta.threads.runs.list(
  "thread_abc123"
)

print(runs)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const runs = await openai.beta.threads.runs.list(
    "thread_abc123"
  );

  console.log(runs);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
{
  "object": "list",
  "data": [\
    {\
      "id": "run_abc123",\
      "object": "thread.run",\
      "created_at": 1699075072,\
      "assistant_id": "asst_abc123",\
      "thread_id": "thread_abc123",\
      "status": "completed",\
      "started_at": 1699075072,\
      "expires_at": null,\
      "cancelled_at": null,\
      "failed_at": null,\
      "completed_at": 1699075073,\
      "last_error": null,\
      "model": "gpt-4-turbo",\
      "instructions": null,\
      "incomplete_details": null,\
      "tools": [\
        {\
          "type": "code_interpreter"\
        }\
      ],\
      "file_ids": [\
        "file-abc123",\
        "file-abc456"\
      ],\
      "metadata": {},\
      "usage": {\
        "prompt_tokens": 123,\
        "completion_tokens": 456,\
        "total_tokens": 579\
      },\
      "temperature": 1.0,\
      "top_p": 1.0,\
      "max_prompt_tokens": 1000,\
      "max_completion_tokens": 1000,\
      "truncation_strategy": {\
        "type": "auto",\
        "last_messages": null\
      },\
      "response_format": "auto",\
      "tool_choice": "auto"\
    },\
    {\
      "id": "run_abc456",\
      "object": "thread.run",\
      "created_at": 1699063290,\
      "assistant_id": "asst_abc123",\
      "thread_id": "thread_abc123",\
      "status": "completed",\
      "started_at": 1699063290,\
      "expires_at": null,\
      "cancelled_at": null,\
      "failed_at": null,\
      "completed_at": 1699063291,\
      "last_error": null,\
      "model": "gpt-4-turbo",\
      "instructions": null,\
      "incomplete_details": null,\
      "tools": [\
        {\
          "type": "code_interpreter"\
        }\
      ],\
      "file_ids": [\
        "file-abc123",\
        "file-abc456"\
      ],\
      "metadata": {},\
      "usage": {\
        "prompt_tokens": 123,\
        "completion_tokens": 456,\
        "total_tokens": 579\
      },\
      "temperature": 1.0,\
      "top_p": 1.0,\
      "max_prompt_tokens": 1000,\
      "max_completion_tokens": 1000,\
      "truncation_strategy": {\
        "type": "auto",\
        "last_messages": null\
      },\
      "response_format": "auto",\
      "tool_choice": "auto"\
    }\
  ],
  "first_id": "run_abc123",
  "last_id": "run_abc456",
  "has_more": false
}
```

## List run steps (v1)  Legacy

gethttps://api.openai.com/v1/threads/{thread\_id}/runs/{run\_id}/steps

Returns a list of run steps belonging to a run.

### Path parameters

thread\_id

string

Required

The ID of the thread the run and run steps belong to.

run\_id

string

Required

The ID of the run the run steps belong to.

### Query parameters

limit

integer

Optional

Defaults to 20

A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order

string

Optional

Defaults to desc

Sort order by the `created_at` timestamp of the objects. `asc` for ascending order and `desc` for descending order.

after

string

Optional

A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include after=obj\_foo in order to fetch the next page of the list.

before

string

Optional

A cursor for use in pagination. `before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj\_foo, your subsequent call can include before=obj\_foo in order to fetch the previous page of the list.

### Returns

A list of [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object) objects.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123/steps \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1"
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

run_steps = client.beta.threads.runs.steps.list(
    thread_id="thread_abc123",
    run_id="run_abc123"
)

print(run_steps)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const runStep = await openai.beta.threads.runs.steps.list(
    "thread_abc123",
    "run_abc123"
  );
  console.log(runStep);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
{
  "object": "list",
  "data": [\
    {\
      "id": "step_abc123",\
      "object": "thread.run.step",\
      "created_at": 1699063291,\
      "run_id": "run_abc123",\
      "assistant_id": "asst_abc123",\
      "thread_id": "thread_abc123",\
      "type": "message_creation",\
      "status": "completed",\
      "cancelled_at": null,\
      "completed_at": 1699063291,\
      "expired_at": null,\
      "failed_at": null,\
      "last_error": null,\
      "step_details": {\
        "type": "message_creation",\
        "message_creation": {\
          "message_id": "msg_abc123"\
        }\
      },\
      "usage": {\
        "prompt_tokens": 123,\
        "completion_tokens": 456,\
        "total_tokens": 579\
      }\
    }\
  ],
  "first_id": "step_abc123",
  "last_id": "step_abc456",
  "has_more": false
}
```

## Retrieve run (v1)  Legacy

gethttps://api.openai.com/v1/threads/{thread\_id}/runs/{run\_id}

Retrieves a run.

### Path parameters

thread\_id

string

Required

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads-v1) that was run.

run\_id

string

Required

The ID of the run to retrieve.

### Returns

The [run](https://platform.openai.com/docs/api-reference/runs-v1/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1"
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

run = client.beta.threads.runs.retrieve(
  thread_id="thread_abc123",
  run_id="run_abc123"
)

print(run)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const run = await openai.beta.threads.runs.retrieve(
    "thread_abc123",
    "run_abc123"
  );

  console.log(run);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
{
  "id": "run_abc123",
  "object": "thread.run",
  "created_at": 1699075072,
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "status": "completed",
  "started_at": 1699075072,
  "expires_at": null,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": 1699075073,
  "last_error": null,
  "model": "gpt-4-turbo",
  "instructions": null,
  "incomplete_details": null,
  "tools": [\
    {\
      "type": "code_interpreter"\
    }\
  ],
  "file_ids": [\
    "file-abc123",\
    "file-abc456"\
  ],
  "metadata": {},
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  },
  "temperature": 1.0,
  "top_p": 1.0,
  "max_prompt_tokens": 1000,
  "max_completion_tokens": 1000,
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "response_format": "auto",
  "tool_choice": "auto"
}
```

## Retrieve run step (v1)  Legacy

gethttps://api.openai.com/v1/threads/{thread\_id}/runs/{run\_id}/steps/{step\_id}

Retrieves a run step.

### Path parameters

thread\_id

string

Required

The ID of the thread to which the run and run step belongs.

run\_id

string

Required

The ID of the run to which the run step belongs.

step\_id

string

Required

The ID of the run step to retrieve.

### Returns

The [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123/steps/step_abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1"
```

```python
1
2
3
4
5
6
7
8
9
10
from openai import OpenAI
client = OpenAI()

run_step = client.beta.threads.runs.steps.retrieve(
    thread_id="thread_abc123",
    run_id="run_abc123",
    step_id="step_abc123"
)

print(run_step)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
import OpenAI from "openai";
const openai = new OpenAI();

async function main() {
  const runStep = await openai.beta.threads.runs.steps.retrieve(
    "thread_abc123",
    "run_abc123",
    "step_abc123"
  );
  console.log(runStep);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
{
  "id": "step_abc123",
  "object": "thread.run.step",
  "created_at": 1699063291,
  "run_id": "run_abc123",
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "type": "message_creation",
  "status": "completed",
  "cancelled_at": null,
  "completed_at": 1699063291,
  "expired_at": null,
  "failed_at": null,
  "last_error": null,
  "step_details": {
    "type": "message_creation",
    "message_creation": {
      "message_id": "msg_abc123"
    }
  },
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  }
}
```

## Modify run (v1)  Legacy

posthttps://api.openai.com/v1/threads/{thread\_id}/runs/{run\_id}

Modifies a run.

### Path parameters

thread\_id

string

Required

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads-v1) that was run.

run\_id

string

Required

The ID of the run to modify.

### Request body

metadata

map

Optional

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

### Returns

The modified [run](https://platform.openai.com/docs/api-reference/runs-v1/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1" \
  -d '{
    "metadata": {
      "user_id": "user_abc123"
    }
  }'
```

```python
1
2
3
4
5
6
7
8
9
10
from openai import OpenAI
client = OpenAI()

run = client.beta.threads.runs.update(
  thread_id="thread_abc123",
  run_id="run_abc123",
  metadata={"user_id": "user_abc123"},
)

print(run)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const run = await openai.beta.threads.runs.update(
    "thread_abc123",
    "run_abc123",
    {
      metadata: {
        user_id: "user_abc123",
      },
    }
  );

  console.log(run);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
{
  "id": "run_abc123",
  "object": "thread.run",
  "created_at": 1699075072,
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "status": "completed",
  "started_at": 1699075072,
  "expires_at": null,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": 1699075073,
  "last_error": null,
  "model": "gpt-4-turbo",
  "instructions": null,
  "incomplete_details": null,
  "tools": [\
    {\
      "type": "code_interpreter"\
    }\
  ],
  "file_ids": [\
    "file-abc123",\
    "file-abc456"\
  ],
  "metadata": {
    "user_id": "user_abc123"
  },
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  },
  "temperature": 1.0,
  "top_p": 1.0,
  "max_prompt_tokens": 1000,
  "max_completion_tokens": 1000,
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "response_format": "auto",
  "tool_choice": "auto"
}
```

## Submit tool outputs to run (v1)  Legacy

posthttps://api.openai.com/v1/threads/{thread\_id}/runs/{run\_id}/submit\_tool\_outputs

When a run has the `status: "requires_action"` and `required_action.type` is `submit_tool_outputs`, this endpoint can be used to submit the outputs from the tool calls once they're all completed. All outputs must be submitted in a single request.

### Path parameters

thread\_id

string

Required

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads-v1) to which this run belongs.

run\_id

string

Required

The ID of the run that requires the tool output submission.

### Request body

tool\_outputs

array

Required

A list of tools for which the outputs are being submitted.

Show properties

stream

boolean or null

Optional

If `true`, returns a stream of events that happen during the Run as server-sent events, terminating when the Run enters a terminal state with a `data: [DONE]` message.

### Returns

The modified [run](https://platform.openai.com/docs/api-reference/runs-v1/object) object matching the specified ID.

DefaultDefaultStreamingStreaming

Example request

curl

```bash
1
2
3
4
5
6
7
8
9
10
11
12
curl https://api.openai.com/v1/threads/thread_123/runs/run_123/submit_tool_outputs \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v1" \
  -d '{
    "tool_outputs": [\
      {\
        "tool_call_id": "call_001",\
        "output": "70 degrees and sunny."\
      }\
    ]
  }'
```

```python
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
from openai import OpenAI
client = OpenAI()

run = client.beta.threads.runs.submit_tool_outputs(
  thread_id="thread_123",
  run_id="run_123",
  tool_outputs=[\
    {\
      "tool_call_id": "call_001",\
      "output": "70 degrees and sunny."\
    }\
  ]
)

print(run)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const run = await openai.beta.threads.runs.submitToolOutputs(
    "thread_123",
    "run_123",
    {
      tool_outputs: [\
        {\
          tool_call_id: "call_001",\
          output: "70 degrees and sunny.",\
        },\
      ],
    }
  );

  console.log(run);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
{
  "id": "run_123",
  "object": "thread.run",
  "created_at": 1699075592,
  "assistant_id": "asst_123",
  "thread_id": "thread_123",
  "status": "queued",
  "started_at": 1699075592,
  "expires_at": 1699076192,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": null,
  "last_error": null,
  "model": "gpt-4-turbo",
  "instructions": null,
  "incomplete_details": null,
  "tools": [\
    {\
      "type": "function",\
      "function": {\
        "name": "get_current_weather",\
        "description": "Get the current weather in a given location",\
        "parameters": {\
          "type": "object",\
          "properties": {\
            "location": {\
              "type": "string",\
              "description": "The city and state, e.g. San Francisco, CA"\
            },\
            "unit": {\
              "type": "string",\
              "enum": ["celsius", "fahrenheit"]\
            }\
          },\
          "required": ["location"]\
        }\
      }\
    }\
  ],
  "file_ids": [],
  "metadata": {},
  "usage": null,
  "temperature": 1.0,
  "top_p": 1.0,
  "max_prompt_tokens": 1000,
  "max_completion_tokens": 1000,
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "response_format": "auto",
  "tool_choice": "auto"
}
```

## Cancel a run (v1)  Legacy

posthttps://api.openai.com/v1/threads/{thread\_id}/runs/{run\_id}/cancel

Cancels a run that is `in_progress`.

### Path parameters

thread\_id

string

Required

The ID of the thread to which this run belongs.

run\_id

string

Required

The ID of the run to cancel.

### Returns

The modified [run](https://platform.openai.com/docs/api-reference/runs-v1/object) object matching the specified ID.

Example request

curl

```bash
1
2
3
4
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123/cancel \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v1" \
  -X POST
```

```python
1
2
3
4
5
6
7
8
9
from openai import OpenAI
client = OpenAI()

run = client.beta.threads.runs.cancel(
  thread_id="thread_abc123",
  run_id="run_abc123"
)

print(run)
```

```javascript
1
2
3
4
5
6
7
8
9
10
11
12
13
14
import OpenAI from "openai";

const openai = new OpenAI();

async function main() {
  const run = await openai.beta.threads.runs.cancel(
    "thread_abc123",
    "run_abc123"
  );

  console.log(run);
}

main();
```

Response

```json
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
{
  "id": "run_abc123",
  "object": "thread.run",
  "created_at": 1699076126,
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "status": "cancelling",
  "started_at": 1699076126,
  "expires_at": 1699076726,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": null,
  "last_error": null,
  "model": "gpt-4-turbo",
  "instructions": "You summarize books.",
  "tools": [\
    {\
      "type": "retrieval"\
    }\
  ],
  "file_ids": [],
  "metadata": {},
  "usage": null,
  "temperature": 1.0,
  "top_p": 1.0,
}
```

## The run object (v1)  Legacy

Represents an execution run on a [thread](https://platform.openai.com/docs/api-reference/threads-v1).

id

string

The identifier, which can be referenced in API endpoints.

object

string

The object type, which is always `thread.run`.

created\_at

integer

The Unix timestamp (in seconds) for when the run was created.

thread\_id

string

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads-v1) that was executed on as a part of this run.

assistant\_id

string

The ID of the [assistant](https://platform.openai.com/docs/api-reference/assistants-v1) used for execution of this run.

status

string

The status of the run, which can be either `queued`, `in_progress`, `requires_action`, `cancelling`, `cancelled`, `failed`, `completed`, or `expired`.

required\_action

object or null

Details on the action required to continue the run. Will be `null` if no action is required.

Show properties

last\_error

object or null

The last error associated with this run. Will be `null` if there are no errors.

Show properties

expires\_at

integer or null

The Unix timestamp (in seconds) for when the run will expire.

started\_at

integer or null

The Unix timestamp (in seconds) for when the run was started.

cancelled\_at

integer or null

The Unix timestamp (in seconds) for when the run was cancelled.

failed\_at

integer or null

The Unix timestamp (in seconds) for when the run failed.

completed\_at

integer or null

The Unix timestamp (in seconds) for when the run was completed.

incomplete\_details

object or null

Details on why the run is incomplete. Will be `null` if the run is not incomplete.

Show properties

model

string

The model that the [assistant](https://platform.openai.com/docs/api-reference/assistants-v1) used for this run.

instructions

string

The instructions that the [assistant](https://platform.openai.com/docs/api-reference/assistants-v1) used for this run.

tools

array

The list of tools that the [assistant](https://platform.openai.com/docs/api-reference/assistants-v1) used for this run.

Show possible types

file\_ids

array

The list of [File](https://platform.openai.com/docs/api-reference/files) IDs the [assistant](https://platform.openai.com/docs/api-reference/assistants-v1) used for this run.

metadata

map

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

usage

temperature

number or null

The sampling temperature used for this run. If not set, defaults to 1.

top\_p

number or null

The nucleus sampling value used for this run. If not set, defaults to 1.

max\_prompt\_tokens

integer or null

The maximum number of prompt tokens specified to have been used over the course of the run.

max\_completion\_tokens

integer or null

The maximum number of completion tokens specified to have been used over the course of the run.

truncation\_strategy

object

Show properties

tool\_choice

string or object

Controls which (if any) tool is called by the model.
`none` means the model will not call any tools and instead generates a message.
`auto` is the default value and means the model can pick between generating a message or calling a tool.
Specifying a particular tool like `{"type": "TOOL_TYPE"}` or `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool.

Show possible types

response\_format

string or object

Specifies the format that the model must output. Compatible with [GPT-4o](https://platform.openai.com/docs/models#gpt-4o), [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4), and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is valid JSON.

**Important:** when using JSON mode, you **must** also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

Show possible types

OBJECT The run object (v1)

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
{
  "id": "run_abc123",
  "object": "thread.run",
  "created_at": 1698107661,
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "status": "completed",
  "started_at": 1699073476,
  "expires_at": null,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": 1699073498,
  "last_error": null,
  "model": "gpt-4-turbo",
  "instructions": null,
  "tools": [{"type": "retrieval"}, {"type": "code_interpreter"}],
  "file_ids": [],
  "metadata": {},
  "incomplete_details": null,
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  },
  "temperature": 1.0,
  "top_p": 1.0,
  "max_prompt_tokens": 1000,
  "max_completion_tokens": 1000,
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "response_format": "auto",
  "tool_choice": "auto"
}
```

## The run step object (v1)  Legacy

Represents a step in execution of a run.

id

string

The identifier of the run step, which can be referenced in API endpoints.

object

string

The object type, which is always `thread.run.step`.

created\_at

integer

The Unix timestamp (in seconds) for when the run step was created.

assistant\_id

string

The ID of the [assistant](https://platform.openai.com/docs/api-reference/assistants-v1) associated with the run step.

thread\_id

string

The ID of the [thread](https://platform.openai.com/docs/api-reference/threads-v1) that was run.

run\_id

string

The ID of the [run](https://platform.openai.com/docs/api-reference/runs-v1) that this run step is a part of.

type

string

The type of run step, which can be either `message_creation` or `tool_calls`.

status

string

The status of the run step, which can be either `in_progress`, `cancelled`, `failed`, `completed`, or `expired`.

step\_details

object

The details of the run step.

Show possible types

last\_error

object or null

The last error associated with this run step. Will be `null` if there are no errors.

Show properties

expired\_at

integer or null

The Unix timestamp (in seconds) for when the run step expired. A step is considered expired if the parent run is expired.

cancelled\_at

integer or null

The Unix timestamp (in seconds) for when the run step was cancelled.

failed\_at

integer or null

The Unix timestamp (in seconds) for when the run step failed.

completed\_at

integer or null

The Unix timestamp (in seconds) for when the run step completed.

metadata

map

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.

usage

OBJECT The run step object (v1)

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
{
  "id": "step_abc123",
  "object": "thread.run.step",
  "created_at": 1699063291,
  "run_id": "run_abc123",
  "assistant_id": "asst_abc123",
  "thread_id": "thread_abc123",
  "type": "message_creation",
  "status": "completed",
  "cancelled_at": null,
  "completed_at": 1699063291,
  "expired_at": null,
  "failed_at": null,
  "last_error": null,
  "step_details": {
    "type": "message_creation",
    "message_creation": {
      "message_id": "msg_abc123"
    }
  },
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  }
}
```

## Streaming (v1)  Legacy

Stream the result of executing a Run or resuming a Run after submitting tool outputs.

You can stream events from the [Create Thread and Run](https://platform.openai.com/docs/api-reference/runs-v1/createThreadAndRun),
[Create Run](https://platform.openai.com/docs/api-reference/runs-v1/createRun), and [Submit Tool Outputs](https://platform.openai.com/docs/api-reference/runs-v1/submitToolOutputs)
endpoints by passing `"stream": true`. The response will be a [Server-Sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events) stream.

Our Node and Python SDKs provide helpful utilities to make streaming easy. Reference the
[Assistants API quickstart](https://platform.openai.com/docs/assistants/overview) to learn more.

## The message delta object (v1)  Legacy

Represents a message delta i.e. any changed fields on a message during streaming.

id

string

The identifier of the message, which can be referenced in API endpoints.

object

string

The object type, which is always `thread.message.delta`.

delta

object

The delta containing the fields that have changed on the Message.

Show properties

OBJECT The message delta object (v1)

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
{
  "id": "msg_123",
  "object": "thread.message.delta",
  "delta": {
    "content": [\
      {\
        "index": 0,\
        "type": "text",\
        "text": { "value": "Hello", "annotations": [] }\
      }\
    ]
  }
}
```

## The run step delta object (v1)  Legacy

Represents a run step delta i.e. any changed fields on a run step during streaming.

id

string

The identifier of the run step, which can be referenced in API endpoints.

object

string

The object type, which is always `thread.run.step.delta`.

delta

object

The delta containing the fields that have changed on the run step.

Show properties

OBJECT The run step delta object (v1)

```JSON
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
{
  "id": "step_123",
  "object": "thread.run.step.delta",
  "delta": {
    "step_details": {
      "type": "tool_calls",
      "tool_calls": [\
        {\
          "index": 0,\
          "id": "call_123",\
          "type": "code_interpreter",\
          "code_interpreter": { "input": "", "outputs": [] }\
        }\
      ]
    }
  }
}
```

## Assistant stream events (v1)  Legacy

Represents an event emitted when streaming a Run.

Each event in a server-sent events stream has an `event` and `data` property:

```text
event: thread.created
data: {"id": "thread_123", "object": "thread", ...}
```

We emit events whenever a new object is created, transitions to a new state, or is being
streamed in parts (deltas). For example, we emit `thread.run.created` when a new run
is created, `thread.run.completed` when a run completes, and so on. When an Assistant chooses
to create a message during a run, we emit a `thread.message.created event`, a
`thread.message.in_progress` event, many `thread.message.delta` events, and finally a
`thread.message.completed` event.

We may add additional events over time, so we recommend handling unknown events gracefully
in your code. See the [Assistants API quickstart](https://platform.openai.com/docs/assistants/overview) to learn how to
integrate the Assistants API with streaming.

thread.created

`data` is a [thread](https://platform.openai.com/docs/api-reference/threads-v1/object)

Occurs when a new [thread](https://platform.openai.com/docs/api-reference/threads-v1/object) is created.

thread.run.created

`data` is a [run](https://platform.openai.com/docs/api-reference/runs-v1/object)

Occurs when a new [run](https://platform.openai.com/docs/api-reference/runs-v1/object) is created.

thread.run.queued

`data` is a [run](https://platform.openai.com/docs/api-reference/runs-v1/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs-v1/object) moves to a `queued` status.

thread.run.in\_progress

`data` is a [run](https://platform.openai.com/docs/api-reference/runs-v1/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs-v1/object) moves to an `in_progress` status.

thread.run.requires\_action

`data` is a [run](https://platform.openai.com/docs/api-reference/runs-v1/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs-v1/object) moves to a `requires_action` status.

thread.run.completed

`data` is a [run](https://platform.openai.com/docs/api-reference/runs-v1/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs-v1/object) is completed.

thread.run.failed

`data` is a [run](https://platform.openai.com/docs/api-reference/runs-v1/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs-v1/object) fails.

thread.run.cancelling

`data` is a [run](https://platform.openai.com/docs/api-reference/runs-v1/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs-v1/object) moves to a `cancelling` status.

thread.run.cancelled

`data` is a [run](https://platform.openai.com/docs/api-reference/runs-v1/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs-v1/object) is cancelled.

thread.run.expired

`data` is a [run](https://platform.openai.com/docs/api-reference/runs-v1/object)

Occurs when a [run](https://platform.openai.com/docs/api-reference/runs-v1/object) expires.

thread.run.step.created

`data` is a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object)

Occurs when a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object) is created.

thread.run.step.in\_progress

`data` is a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object)

Occurs when a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object) moves to an `in_progress` state.

thread.run.step.delta

`data` is a [run step delta](https://platform.openai.com/docs/api-reference/assistants-streaming-v1/run-step-delta-object)

Occurs when parts of a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object) are being streamed.

thread.run.step.completed

`data` is a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object)

Occurs when a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object) is completed.

thread.run.step.failed

`data` is a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object)

Occurs when a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object) fails.

thread.run.step.cancelled

`data` is a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object)

Occurs when a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object) is cancelled.

thread.run.step.expired

`data` is a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object)

Occurs when a [run step](https://platform.openai.com/docs/api-reference/runs-v1/step-object) expires.

thread.message.created

`data` is a [message](https://platform.openai.com/docs/api-reference/messages-v1/object)

Occurs when a [message](https://platform.openai.com/docs/api-reference/messages-v1/object) is created.

thread.message.in\_progress

`data` is a [message](https://platform.openai.com/docs/api-reference/messages-v1/object)

Occurs when a [message](https://platform.openai.com/docs/api-reference/messages-v1/object) moves to an `in_progress` state.

thread.message.delta

`data` is a [message delta](https://platform.openai.com/docs/api-reference/assistants-streaming-v1/message-delta-object)

Occurs when parts of a [Message](https://platform.openai.com/docs/api-reference/messages-v1/object) are being streamed.

thread.message.completed

`data` is a [message](https://platform.openai.com/docs/api-reference/messages-v1/object)

Occurs when a [message](https://platform.openai.com/docs/api-reference/messages-v1/object) is completed.

thread.message.incomplete

`data` is a [message](https://platform.openai.com/docs/api-reference/messages-v1/object)

Occurs when a [message](https://platform.openai.com/docs/api-reference/messages-v1/object) ends before it is completed.

error

`data` is an [error](https://platform.openai.com/docs/guides/error-codes#api-errors)

Occurs when an [error](https://platform.openai.com/docs/guides/error-codes#api-errors) occurs. This can happen due to an internal server error or a timeout.

done

`data` is `[DONE]`

Occurs when a stream ends.