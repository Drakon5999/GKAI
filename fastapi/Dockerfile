FROM python:3.10-bullseye
ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /fastapi
COPY . .
RUN pip install -r requirements.txt
RUN pip install python-multipart

ENTRYPOINT ["uvicorn", "main:app",  "--host", "0.0.0.0", "--port", "8800"]