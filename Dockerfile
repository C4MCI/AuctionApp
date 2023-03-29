FROM python:3.7-alpine

# 
WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers mariadb-connector-c-dev

COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY . /code/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]