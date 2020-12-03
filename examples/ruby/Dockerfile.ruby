FROM ubuntu:latest

ENV WORK_DIR="/cyberark"
RUN mkdir $WORK_DIR && \
    mkdir $WORK_DIR/client
WORKDIR $WORK_DIR

RUN apt-get update && \
    apt-get install -y ruby-full \
                       build-essential \
                       ruby-dev \
                       curl

COPY ./examples/ruby/ruby_client.rb .
COPY ./out/ruby .

RUN gem build ./openapi_client && \
    gem install ./openapi_client-1.0.0.gem
