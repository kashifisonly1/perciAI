FROM node:12.14.0-buster-slim as webpack
LABEL maintainer="Britton Upchurch <tobritton@gmail.com>"

WORKDIR /app/assets

COPY assets/package.json assets/*yarn* ./

ENV BUILD_DEPS="build-essential" \
    APP_DEPS=""

RUN apt-get update \
  && apt-get install -y ${BUILD_DEPS} ${APP_DEPS} --no-install-recommends \
  && yarn install \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf /usr/share/doc && rm -rf /usr/share/man \
  && apt-get purge -y --auto-remove ${BUILD_DEPS} \
  && apt-get clean

COPY assets .

ARG NODE_ENV="production"
ENV NODE_ENV="${NODE_ENV}"

RUN if [ "${NODE_ENV}" != "development" ]; then \
  yarn run build; else mkdir -p /app/public; fi

CMD ["bash"]

#

FROM python:3.8.3-slim-buster as app
LABEL maintainer="Britton Upchurch <tobritton@gmail.com>"

WORKDIR /app

COPY requirements.txt requirements.txt

ENV BUILD_DEPS="build-essential" \
    APP_DEPS="curl libpq-dev" \
    PORT=8000

RUN apt-get update \
  && apt-get install -y ${BUILD_DEPS} ${APP_DEPS} --no-install-recommends \
  && pip install -r requirements.txt \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf /usr/share/doc && rm -rf /usr/share/man \
  && apt-get purge -y --auto-remove ${BUILD_DEPS} \
  && apt-get clean

# Install Google Cloud tools - Debian https://cloud.google.com/storage/docs/gsutil_install#deb
ENV CLOUD_SDK_REPO="cloud-sdk-stretch"
RUN echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && apt-get install -y google-cloud-sdk

# Setup Google Service Account
COPY service-account.json service-account.json
ENV GOOGLE_APPLICATION_CREDENTIALS="service-account.json"

RUN gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

# Copy the models in
RUN gsutil cp -r gs://perciapp-processor/models /app/perciapp

ARG FLASK_ENV="production"
ENV FLASK_ENV="${FLASK_ENV}" \
    FLASK_APP="perciapp.app" \
    PYTHONUNBUFFERED="true"

COPY --from=webpack /app/public /public

COPY . .

RUN if [ "${FLASK_ENV}" != "development" ]; then \
  ln -s /public /app/public && flask digest compile && rm -rf /app/public; fi

RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]

EXPOSE 8000

CMD ["gunicorn", "-c", "python:config.gunicorn", "perciapp.app:create_app()"]
