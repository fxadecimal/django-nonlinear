# Pull base image
FROM python:3.12.1-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set work directory called `app`
RUN mkdir -p /code
WORKDIR /code

# Install dependencies
# COPY sample_project/requirements.txt /tmp/requirements.txt
COPY . /code/

RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /code/sample_project/requirements.txt && \
    rm -rf /root/.cache/

# install nonlinear
RUN pip install .

WORKDIR /code/sample_project

CMD python3 ./manage.py runserver 0.0.0.0:8000