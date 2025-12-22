FROM python:3.14-alpine3.23

WORKDIR /usr/src/app

# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# ensure python output is sent directly to the terminal
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY req.txt /usr/src/app/req.txt
RUN pip install -r req.txt

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

COPY . /usr/src/app/

# this run everytime when the container start
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]