FROM python:3.7-alpine

RUN apk add python python-dev py-pip git
RUN pip install pyyaml redis requests sqlalchemy

ARG NOCACHE=0
RUN git clone https://github.com/pieterbork/Jarvis.git
WORKDIR Jarvis

CMD ["python", "run.py", "-c", "/etc/jarvis/jarvis.cfg"]
