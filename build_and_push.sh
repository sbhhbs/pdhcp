docker buildx build \
  --platform linux/amd64 \
  --push -t sbhhbs/pdhcp:`git rev-parse --short HEAD` -t sbhhbs/pdhcp:latest .