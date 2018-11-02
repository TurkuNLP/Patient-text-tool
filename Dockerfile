FROM ubuntu:18.04

MAINTAINER Antti Virtanen <sajvir@utu.fi>

ENV TERM xterm-256color

# Install required packages, setup timezone.
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y lsof tar tzdata default-jdk python3 python3-pip curl
RUN ln -fs /usr/share/zoneinfo/Europe/Helsinki /etc/localtime
RUN dpkg-reconfigure --frontend noninteractive tzdata 1>&2
RUN apt-get install -y git gnupg2 node.js
RUN useradd -m appuser -d /home/appuser

WORKDIR /home/appuser/

# Install Ruby.
RUN gpg2 --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 7D2BAF1CF37B13E2069D6956105BD0E739499BDB
RUN \curl -sSL https://get.rvm.io | bash -s stable --ruby --rails

# Setting up Solr.
#USER appuser
RUN curl http://www.nic.funet.fi/pub/mirrors/apache.org/lucene/solr/7.5.0/solr-7.5.0.tgz -o solr-7.5.0.tgz
RUN tar xf solr-7.5.0.tgz
#RUN /home/appuser/solr-7.5.0/bin/solr start
#RUN /home/appuser/solr-7.5.0/bin/solr create_core -c core1
#RUN /home/appuser/solr-7.5.0/bin/solr stop
#USER root
RUN rm solr-7.5.0.tgz

# Add files.
ADD blacklight/ /home/appuser/blacklight
ADD solr /home/appuser/solr
ADD solrglue /home/appuser/solrglue
ADD index.py /home/appuser/
ADD start_all.sh /home/appuser/

RUN cp -r /home/appuser/solr/* /home/appuser/solr-7.5.0/

#RUN chown -R appuser:appuser /home/appuser/solr-7.5.0/* /home/appuser/solrglue/data

# Setup docker volumes for modifiable data.
#VOLUME /home/appuser/solrglue/data
#VOLUME /home/appuser/solr-7.5.0/server/solr/core1/data

#WORKDIR /home/appuser/

# Setup blacklight and all its dependencies.
RUN bash -c "source /usr/local/rvm/scripts/rvm; gem install bundler"
RUN bash -c 'source /usr/local/rvm/scripts/rvm; rails new search_app -m https://raw.github.com/projectblacklight/blacklight/master/template.demo.rb'

RUN cp -r /home/appuser/blacklight/config /home/appuser/search_app
RUN cp -r /home/appuser/blacklight/app /home/appuser/search_app

RUN chown -R appuser:appuser /home/appuser/*

USER appuser

# Setup python 
RUN pip3 install -U -r /home/appuser/solrglue/requirements.txt

VOLUME /home/appuser/solrglue/data
VOLUME /home/appuser/solr-7.5.0/server/solr/core1/data

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV FLASK_APP=solrglue.py

# Expose ports to the world outside the container.
EXPOSE 5000
EXPOSE 8983
EXPOSE 3000

WORKDIR /home/appuser/

# Define the default command to be run when the container starts. This starts all the necessary servers.
CMD bash -c 'source /usr/local/rvm/scripts/rvm; /home/appuser/start_all.sh'
