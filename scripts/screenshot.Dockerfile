FROM mongo:7
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash xvfb xterm imagemagick x11-utils fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
