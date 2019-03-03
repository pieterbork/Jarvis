FROM alpine:latest

RUN apk add python python-dev py-pip git
RUN git clone https://github.com/pieterbork/Jarvis.git

WORKDIR Jarvis

CMD ["python run.py -c /jarvis.cfg"]
