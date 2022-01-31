import os
from typing import Optional
import time

from fastapi import FastAPI
from transformers import pipeline
from pydantic import BaseModel, PositiveInt, constr

import ray
from ray import serve

app = FastAPI()


class Request(BaseModel):
    text: constr(min_length=1, strip_whitespace=True)
    min_length: Optional[PositiveInt]
    max_length: Optional[PositiveInt]


@serve.deployment
@serve.ingress(app)
class Summarizer:
    def __init__(self):
        self.summarize = pipeline("summarization", model="t5-small")

    @app.post("/")
    def get_summary(self, payload: Request):
        summary_list = self.summarize(
            payload.text,
            min_length=payload.min_length or 0,
            max_length=payload.max_length or 256,
        )
        summary = summary_list[0]["summary_text"]
        return summary

ray.init(address="auto")
serve.start(
    http_options={"host": "0.0.0.0", "port": int(os.environ.get("PORT", "8000"))}
)
Summarizer.deploy()

# Block the container process from exit
while True:
    time.sleep(5)
