FROM python:3

# For debugging
RUN apt-get update
RUN apt-get install -y vim nano postgresql-client

# Some stuff that everyone has been copy-pasting
# since the dawn of time.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy all our files into the image.
RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install -U pip
RUN pip install -Ur requirements.txt

COPY ./ /code/
WORKDIR /code

RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]
