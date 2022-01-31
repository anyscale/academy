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
docker tag your-repo/container-name gcr.io/project-name/container-name
docker push gcr.io/project-name/container-name

gcloud run deploy serve-demo \
  --image=gcr.io/project-name/container-name \
  --allow-unauthenticated \
  --platform=managed \
  --region=us-central1 \
  --project=project-name
```


