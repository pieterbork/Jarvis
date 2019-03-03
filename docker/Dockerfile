FROM alpine:latest

RUN apk add python python-dev py-pip git
RUN git clone https://github.com/pieterbork/Jarvis.git

WORKDIR Jarvis

RUN pip install -r requirements.txt

RUN addgroup -S -g 2000 jarvis && \
    adduser -S -u 2000 -G jarvis jarvis

USER jarvis

CMD ["python", "run.py", "-c", "/etc/jarvis/jarvis.cfg"]
