FROM python:3.7-alpine

RUN apk add python python-dev py-pip git
RUN pip install pyyaml redis requests sqlalchemy

RUN addgroup -g 2004 jarvis \
    && adduser -u 2004 -G jarvis -D jarvis

ARG NOCACHE=0
RUN mkdir src && chown jarvis:jarvis src
WORKDIR src
RUN git clone https://github.com/pieterbork/Jarvis.git
WORKDIR Jarvis

CMD ["python", "run.py", "-c", "/etc/jarvis/jarvis.cfg"]
