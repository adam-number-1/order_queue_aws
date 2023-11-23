FROM python:3.11-alpine

# making directory for the app
RUN mkdir /app

# making directory for the credentials
RUN mkdir -p /root/.aws

# copying requirements first to cache this layer
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# make aws config 
RUN echo '[default]' > /root/.aws/config
RUN echo 'region = us-east-1' >> /root/.aws/config

# copy the rest of the app
COPY . /app

#starting the app
WORKDIR /app
ENTRYPOINT [ "python3", "-um", "order_wsgi.main"]

# default parameters for the app
CMD ["localhost:8080", "localhost:6379"]