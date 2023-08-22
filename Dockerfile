FROM python:3.10

# Setup Timezone
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ='Europe/Oslo'
RUN apt-get update && apt-get install -y tzdata git
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV WEBHOOK_SECRET='secret'

RUN git clone https://github.com/sondregronas/taafis && \
    pip install -r taafis/requirements.txt

RUN echo "git pull && pip install -r taafis/requirements.txt && python app.py" > /entrypoint.sh && chmod +x /entrypoint.sh

WORKDIR /taafis
EXPOSE 8000
CMD ["/entrypoint.sh"]