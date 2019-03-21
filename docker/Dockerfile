FROM alpine:latest

RUN apk add python python-dev py-pip git

WORKDIR Jarvis

RUN pip install bs4 googlevoice pyyaml requests sqlalchemy

ARG NOCACHE=0

RUN git clone https://github.com/pieterbork/Jarvis.git

CMD ["python", "run.py", "-c", "/etc/jarvis/jarvis.cfg"]
