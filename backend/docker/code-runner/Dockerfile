FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        nodejs \
        npm \
        bash \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 10001 -s /usr/sbin/nologin sandbox

WORKDIR /sandbox
USER sandbox

CMD ["bash"]