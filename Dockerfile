# syntax=docker/dockerfile:1
#My image inherites from "python" image
FROM python:3.9-bullseye
WORKDIR /app
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY requirements.txt requirements.txt
#Run this command in the container
RUN pip3 install -r requirements.txt
COPY . .
# Run command in container
CMD ["python3", "main.py"]
