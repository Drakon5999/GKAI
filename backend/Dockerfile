FROM python:3.10-bullseye
ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /fastapi
COPY . .
RUN apt-get update && \
    apt-get install ffmpeg libsm6 libxext6 -y
RUN pip install -r requirements.txt

ENTRYPOINT ["uvicorn", "main:app",  "--host", "0.0.0.0"]
