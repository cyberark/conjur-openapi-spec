FROM ubuntu:latest
ARG namespace
MAINTAINER CyberArk

ENV INSTALL_DIR=/opt/conjur-openapi-spec

RUN apt-get update && \
    apt-get install -y bash \
                       binutils \
                       build-essential \
                       git \
                       jq \
                       python3 \
                       python3-dev \
                       python3-pip

RUN mkdir -p $INSTALL_DIR
WORKDIR $INSTALL_DIR

COPY ./requirements.txt $INSTALL_DIR/
RUN pip3 install -r requirements.txt

COPY . $INSTALL_DIR

RUN pip3 install -e out/oss/python/

ENTRYPOINT [ "/bin/bash", "-l", "-c" ]
CMD [ "sleep 9999" ]