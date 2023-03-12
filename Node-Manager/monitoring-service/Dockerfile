FROM python:3.8.16

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./monitoring-service.py ./

CMD ["sudo python3", "./monitoring-service.py"]