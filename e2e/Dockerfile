FROM mcr.microsoft.com/playwright:v1.58.2-jammy

WORKDIR /e2e

COPY e2e/ .

RUN npm install

RUN npx playwright install

CMD ["tail", "-f", "/dev/null"]
