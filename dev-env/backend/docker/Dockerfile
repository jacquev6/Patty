FROM python:3.13

ARG USER_ID
ARG GROUP_ID
RUN set -x \
 && (groupadd --gid $GROUP_ID patty || true) \
 && useradd --uid $USER_ID --gid $GROUP_ID --create-home --shell /bin/bash patty

USER patty
ENV PATH=$PATH:/home/patty/.local/bin
