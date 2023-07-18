# aify

### Write a YAML file to ship your AI application in seconds

🛠️ AI-native application framework and runtime, simply write a YAML file

🤖 Ready-to-use AI chatbot UI

**Dependencies**

* [microsoft/guidance](https://github.com/microsoft/guidance) as the core prompt engine
* [Uvicorn](https://www.uvicorn.org/), [Starlette](https://www.starlette.io/), [FastAPI](https://fastapi.tiangolo.com/) as the server

**TODO**

* API documentation
* Authorization
* Deploy to cloud providers

## Install

```
pip install aify
```

## Run your AI apps:

Create a directory for apps:
```
mkdir ./apps
cd ./apps
```

Run:
```
aify run
```

Open your web browser and visit: [http://127.0.0.1:2000](http://127.0.0.1:2000)


## Create a chatbot

Create a YAML file: **chatbot.yaml**

Paste this content:

```
title: Chatbot

model:
  vendor: openai
  name: gpt-3.5-turbo
  params:
    api_key: <YOUR_OPENAI_API_KEY>

prompt: |
  {{#system~}}
  You are a helpful and terse assistant.
  {{~/system}}

  {{#each (memory.read program_name session_id n=3)}}
  {{~#if this.role == 'user'}}
  {{#user~}}
  {{this.content}}
  {{~/user}}
  {{/if~}}
  {{~#if this.role == 'assistant'}}
  {{#assistant~}}
  {{this.content}}
  {{~/assistant}}
  {{/if~}}
  {{~/each}}

  {{#user~}}
  {{prompt}}
  {{memory.save program_name session_id 'user' prompt}}
  {{~/user}}

  {{#assistant~}}
  {{gen 'answer' temperature=0 max_tokens=2000}}
  {{memory.save program_name session_id 'assistant' answer}}
  {{~/assistant}}

variables:
  - name: prompt
    type: input
  - name: answer
    type: output
```

Refresh your browser, and you will get your chatbot. Now, you can talk to it.

📝 More examples: https://github.com/shellc/aify/tree/main/examples

## Webui screenshot

![Webui screenshot](./docs/assets/images/screenshots/aify_webui_screenshot.png)