FROM python:3.10-slim

#
WORKDIR /app

#
COPY ./requirements.txt  ./app/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r ./app/requirements.txt

#
COPY ./app ./app

#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
FROM python:3.10-slim

#
WORKDIR /app

#
COPY ./requirements.txt  ./app/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r ./app/requirements.txt

#
COPY ./app ./app

#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]