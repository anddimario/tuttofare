# Use an official Python runtime as a parent image
FROM python:3.7

# todo: install and start ssh-agent
RUN pip install pipenv

COPY . .

RUN pipenv install

RUN chmod +x entrypoint.sh

#CMD ["pipenv", "run", "python", "relive.py"]
ENTRYPOINT [ "./entrypoint.sh" ]