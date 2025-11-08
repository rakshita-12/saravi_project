# -------------------------------
# Base image with compilers/interpreters
# -------------------------------
FROM ubuntu:22.04

# Avoid interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required languages and tools
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    openjdk-17-jdk \
    gcc \
    g++ \
    time \
    curl \
    && apt clean

# Create a working directory
WORKDIR /app

# Copy your evaluator script
COPY local_ai_evaluator.py /app/

# Install Python dependencies
RUN pip install requests

# Default command
CMD ["python3", "local_ai_evaluator.py"]
