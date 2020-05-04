FROM python:3.7-alpine

RUN apk add python python-dev py-pip
RUN pip install --upgrade pip pyyaml redis requests sqlalchemy

RUN addgroup -g 2004 jarvis \
    && adduser -u 2004 -G jarvis -D jarvis

ARG NOCACHE=0
COPY . /

CMD ["python", "run.py", "-c", "/etc/jarvis/jarvis.cfg"]
