# Use an official Python runtime as a parent image
FROM python:3.7

RUN apt-get install pipenv

# todo: install and start ssh-agent

COPY . .

RUN pipenv install

CMD ["pipenv", "run", "python", "relive.py"]
