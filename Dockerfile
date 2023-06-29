FROM python:3.11

WORKDIR /app
ENV PYHTONUNBUFFERED=1
RUN apt-get update \
 && apt-get install -y ffmpeg\
 && apt-get -y clean \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp
RUN apt-get update && apt-get install -y portaudio19-dev
RUN pip install --upgrade pip 
RUN pip install -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt
COPY . .


CMD ["python3", "./main.py"]
