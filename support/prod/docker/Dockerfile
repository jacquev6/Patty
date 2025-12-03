ARG FRONTEND_DEPENDENCIES_IMAGE=frontend-dependencies
ARG BACKEND_DEPENDENCIES_IMAGE=backend-dependencies

FROM node:22 AS frontend-dependencies

WORKDIR /app

ADD frontend/package.json .
ADD frontend/package-lock.json .

RUN npm install

FROM $FRONTEND_DEPENDENCIES_IMAGE AS frontend-code

RUN mkdir -p /backend/generated
ADD backend/generated/adapted-exercise-schema.json /backend/generated
ADD frontend .


FROM frontend-code AS frontend-builder
ENV PATTY_ENTRY_POINT_NAME=frontend
RUN test ! -e src/frontend/public/pdf.worker.min.js
RUN cp node_modules/pdfjs-dist/build/pdf.worker.min.mjs src/frontend/public/pdf.worker.min.js
RUN npx vite build


FROM frontend-code AS adaptation-export-template-builder
ENV PATTY_ENTRY_POINT_NAME=export/adaptation
RUN npx vite build


FROM frontend-code AS batch-export-template-builder
ENV PATTY_ENTRY_POINT_NAME=export/batch
RUN npx vite build


FROM frontend-code AS textbook-export-template-builder
ENV PATTY_ENTRY_POINT_NAME=export/textbook
RUN npx vite build


FROM python:3.12-slim AS backend-dependencies

RUN set -x \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
      libgl1 \
      libglib2.0-bin \
      poppler-utils \
      postgresql-client \
 && true

WORKDIR /app

ADD backend/requirements-10-torch.txt .
RUN pip install -r requirements-10-torch.txt

ADD backend/requirements-20-main.txt .
RUN pip install -r requirements-20-main.txt uvicorn

# Create ~/.config/Ultralytics now to avoid verbose messages later
RUN mkdir ~/.config && python -c 'import ultralytics' && test -d ~/.config/Ultralytics


FROM nginx:alpine AS final-frontend

RUN rm /etc/nginx/conf.d/default.conf /usr/share/nginx/html/*.html
ADD support/prod/docker/frontend.conf /etc/nginx/conf.d/frontend.conf
ADD --chmod=777 support/prod/docker/40-substitute.sh /docker-entrypoint.d/40-substitute.sh
COPY --from=frontend-builder /app/dist /usr/share/nginx/templates/frontend


FROM $BACKEND_DEPENDENCIES_IMAGE AS final-backend

# @todo Run `./prod.sh pre-warm-build-cache` and remove next line
RUN pip install json-repair==0.54.2 PyMuPDF==1.26.6

ADD backend .
ARG PATTY_VERSION
RUN echo "PATTY_VERSION = \"${PATTY_VERSION}\"" >patty/version.py

COPY --from=adaptation-export-template-builder /app/dist/index.html /app/patty/export/templates/adaptation/index.html
COPY --from=batch-export-template-builder /app/dist/index.html /app/patty/export/templates/batch/index.html
COPY --from=textbook-export-template-builder /app/dist/index.html /app/patty/export/templates/textbook/index.html

CMD ["uvicorn", "patty.asgi:app", "--host", "0.0.0.0", "--port", "80"]
