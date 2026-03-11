FROM registry.lnds.lu/library/rhel-nodejs:20 AS build
USER 0

WORKDIR /code/client

COPY ./app/client /code/client

RUN echo "\nVITE_APP_BUILD_TIME=$(date -u +'%Y-%m-%dT%H:%M:%SZ')\n" >> .env.production

RUN npm install

RUN npm run build

COPY documentation/package.json documentation/package-lock.json /code/documentation/

WORKDIR /code/documentation

RUN npm ci --ignore-scripts

COPY ./documentation /code/documentation

RUN npm run build

RUN cp -r /code/documentation/build/* /code/client/public/docs/

FROM registry.lnds.lu/library/rhel-python:3.12
USER 0

WORKDIR /code

COPY ./app /code

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --from=build --chown=1001:1001 /code/client/dist/. /code/client/dist/

COPY --from=build --chown=1001:1001 /code/client/public/docs /code/client/public/docs

USER 1001

# Set default logging format to JSON for production
ENV LOG_FORMAT=json

EXPOSE 8000

# Use uvicorn with log config that propagates to our configured root logger
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--log-config", "/code/uvicorn_log_config.json"]
