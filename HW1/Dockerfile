FROM python:3.12
WORKDIR /HW1_docker
COPY requirements.txt /HW1_docker/requirements.text
COPY /HomeWork1.py /HW1_docker/hw1.py

RUN pip install -r /HW1_docker/requirements.text

CMD ["uvicorn", "hw1:app", "--host", "0.0.0.0", "--port", "80"]
