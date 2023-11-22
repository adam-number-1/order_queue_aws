FROM python:3.11-alpine

# making directory for the app
RUN mdkir /app

# copying requirements first to cache this layer
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# copy the rest of the app
COPY . /app

#starting the app
WORKDIR /app
ENTRYPOINT [ "python3", "-m", "order_wsgi.main"]

# default parameters for the app
CMD ["localhost:8080", "localhost:6379"]