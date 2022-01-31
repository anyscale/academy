This directory contains example of the containerized application. 

### Build
You can build the container image using
```bash
docker build -t your-repo/container-name .
```

### Test
You can test the container using
```bash
docker run -it -p 8000:8000 your-repo/container-name
```
then
```bash
python test-query.py
```

### Deploy to Cloud Run
The best way to deploy your Ray application would be using [Anyscale](anyscale.com). Since Anyscale still requires sign up to deploy, you can use Google Cloud Run for quick demo. 

Note: you might need to enable [artifact registry API](https://console.cloud.google.com/marketplace/product/google/artifactregistry.googleapis.com) to push to gcr.io. 

```bash
# login to gcloud cli
gcloud auth login 

# configure the project if necessary
# gcloud config set project PROJECT_ID

# configure docker to push to google cloud
gcloud auth configure-docker

# push to google container registry
$ docker tag your-repo/container-name gcr.io/project-name/container-name
$ docker push gcr.io/project-name/container-name

$ gcloud run deploy sample-demo \
    --image=gcr.io/project-name/container-name \
    --allow-unauthenticated \
    --port=8000 \
    --concurrency=80 \
    --cpu=4 \
    --memory=8192Mi \
    --platform=managed \
    --region=us-central1 \
    --project=project-name

Deploying container to Cloud Run service [sample-demo] in project [simon-sandbox-329822] region [us-central1]
✓ Deploying... Done.
  ✓ Creating Revision...
  ✓ Routing traffic...
Done.
Service [sample-demo] revision [sample-demo-00010-mog] has been deployed and is serving 100 percent of traffic.
Service URL: https://sample-demo-qosxokjdva-uc.a.run.app

$ SERVE_HOST=https://sample-demo-qosxokjdva-uc.a.run.app python test-query.py
"two astronauts steered their fragile lunar"
```


