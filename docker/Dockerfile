FROM alpine:latest

RUN apk add python python-dev py-pip git
RUN pip install bs4 googlevoice pyyaml requests sqlalchemy

ARG NOCACHE=0
RUN git clone https://github.com/pieterbork/Jarvis.git
WORKDIR Jarvis

CMD ["python", "run.py", "-c", "/etc/jarvis/jarvis.cfg"]
