FROM golang:1.21-bullseye as go-builder

# Install Go tools
RUN go install honnef.co/go/tools/cmd/staticcheck@latest
RUN go install golang.org/x/lint/golint@latest

FROM python:3.10-slim

# Copy Go tools from go-builder
COPY --from=go-builder /go/bin/staticcheck /usr/local/bin/
COPY --from=go-builder /go/bin/golint /usr/local/bin/

# Install Go
RUN apt-get update && \
  apt-get install -y wget git gcc g++ && \
  wget https://golang.org/dl/go1.21.0.linux-amd64.tar.gz && \
  tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz && \
  rm go1.21.0.linux-amd64.tar.gz && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Add Go to PATH
ENV PATH="/usr/local/go/bin:${PATH}"

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Create directory for repo clones
RUN mkdir -p /app/repo

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
  REPO_PATH=/app/repo \
  GOPATH="/go" \
  PATH="/go/bin:/usr/local/go/bin:${PATH}"

# Expose the port
EXPOSE 8000

# Default command (can be overridden)
CMD ["python", "go_main.py", "--mode", "server"]
