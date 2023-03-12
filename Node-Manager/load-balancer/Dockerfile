FROM python:3.8.16

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./load-balancer.py ./

CMD ["python3", "./load-balancer.py"]