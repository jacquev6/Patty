# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

FROM node:22

RUN set -x \
 && rm -f /etc/apt/apt.conf.d/docker-clean \
 && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' >/etc/apt/apt.conf.d/keep-cache

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    set -x \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
      chromium \
      firefox-esr \
      libasound2 \
      libgbm-dev \
      libgtk-3-0 \
      libgtk2.0-0 \
      libnotify-dev \
      libnss3 \
      libxss1 \
      libxtst6 \
      xauth \
      xvfb \
 && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
      fonts-noto \
 && true

RUN deluser --remove-all-files node

ARG USER_ID
ARG GROUP_ID
RUN set -x \
 && (groupadd --gid $GROUP_ID patty || true) \
 && useradd --uid $USER_ID --gid $GROUP_ID --create-home --shell /bin/bash patty

USER patty
