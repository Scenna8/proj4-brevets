FROM python:3
LABEL "Jack Abram"="jabram@uoregon.edu"
RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["flask_brevets.py"]
