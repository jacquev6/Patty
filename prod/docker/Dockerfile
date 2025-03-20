FROM node:22 AS frontend-dependencies

WORKDIR /app

ADD frontend/package.json .
ADD frontend/package-lock.json .

RUN npm install


FROM frontend-dependencies AS frontend-builder

RUN mkdir /backend
ADD backend/adapted-exercise-schema.json /backend
ADD frontend .

RUN npx vite build


FROM python:3.13-slim AS backend-dependencies

WORKDIR /app

ADD backend/requirements-run.txt .

RUN pip install -r requirements-run.txt uvicorn


FROM nginx:alpine AS final-frontend

RUN rm /etc/nginx/conf.d/default.conf /usr/share/nginx/html/*.html
ADD prod/docker/frontend.conf /etc/nginx/conf.d/frontend.conf
COPY --from=frontend-builder /app/dist /usr/share/nginx/html/frontend


FROM backend-dependencies AS final-backend

ADD backend .

CMD ["uvicorn", "patty.asgi:app", "--host", "0.0.0.0", "--port", "80"]
