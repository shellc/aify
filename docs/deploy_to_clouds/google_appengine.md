# Deploy to google app engine

You need to install and configure your Google Cloud CLI before deploying your apps to Google Cloud App Engine. [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)

Examples: [https://github.com/shellc/aify/tree/main/examples](https://github.com/shellc/aify/tree/main/examples)

```

cd examples

cp deploy-to-google-appengine/requirements.txt .

gcloud app deploy ./deploy-to-google-appengine/index.yaml

gcloud app deploy --appyaml ./deploy-to-google-appengine/app.yaml

```

Make sure that the memory module in your app template is specified as `aify.memories.google_cloud_datastore`. You can also set it as an environment variable in the .env file.

.env:
```bash

AIFY_MEMORY_STORAGE=aify.memories.google_cloud_datastore

```

your_app_template.yaml:
```

modules:
  memory: $AIFY_MEMORY_STORAGE

```

Notice: Google Cloud App Engine does not support streaming responses, so aify does not either when it is deployed on Google Cloud App Engine. 

* [https://cloud.google.com/appengine/docs/standard/how-requests-are-handled?tab=python#streaming_responses](https://cloud.google.com/appengine/docs/standard/how-requests-are-handled?tab=python#streaming_responses)
* [https://cloud.google.com/appengine/docs/flexible/how-requests-are-handled?hl=zh-cn&tab=python#x-accel-buffering](https://cloud.google.com/appengine/docs/flexible/how-requests-are-handled?hl=zh-cn&tab=python#x-accel-buffering)