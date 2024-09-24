FROM python:3.9-slim

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl build-essential \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

COPY dist/*.whl /

# hadolint ignore=DL3013
RUN pip --no-cache-dir install /*.whl

CMD ["tuxlava", "--help"]
