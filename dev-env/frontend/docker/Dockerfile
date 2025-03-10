FROM node:22

RUN deluser --remove-all-files node

ARG USER_ID
ARG GROUP_ID
RUN set -x \
 && (groupadd --gid $GROUP_ID patty || true) \
 && useradd --uid $USER_ID --gid $GROUP_ID --create-home --shell /bin/bash patty

USER patty
