FROM python:3.8-buster

COPY explorer.py helpers.py requirements.txt /app/

WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "explorer.py" ]