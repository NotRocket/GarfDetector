FROM python:3.12

WORKDIR /usr/src/garfdetector

COPY ["garf-producer.py","client.properties", "requirements.txt", "./"]

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install -r requirements.txt

CMD ["python", "garf-producer.py"]