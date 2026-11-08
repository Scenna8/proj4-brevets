# Python 3.9 is the newest version the `nose` test runner supports.
FROM python:3.9-slim
LABEL "Jack Abram"="jabram@uoregon.edu"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 5001
ENTRYPOINT ["python"]
CMD ["flask_brevets.py"]
