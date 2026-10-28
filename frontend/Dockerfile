# Build from repository ROOT so synthetic evaluation metrics are available to the UI.
# docker build -f frontend/Dockerfile -t transactionshield-frontend:ci .
FROM node:20-alpine AS builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
COPY artifacts/models/metrics.json /app/artifacts/models/metrics.json
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=builder /app/frontend/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
