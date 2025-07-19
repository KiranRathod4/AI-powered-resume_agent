#!/bin/bash
# exit if any command fails 
set -e

# === Configurable variables ===
ECR_REGISTRY=${ECR_REGISTRY}
ECR_REPOSITORY=${ECR_REPOSITORY}
IMAGE_TAG=${IMAGE_TAG}
CONTAINER_NAME="streamlit-container"
PORT="8501"

# === Safety check ===
if [ -z "$ECR_REGISTRY" ] || [ -z "$ECR_REPOSITORY" ] || [ -z "$IMAGE_TAG" ]; then
  echo "Usage: ./deploy_container.sh <ECR_REGISTRY> <ECR_REPOSITORY> <IMAGE_TAG>"
  exit 1
fi

echo "🔄 Pulling image from ECR..."
docker pull "$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"

echo "🧹 Cleaning up old container if exists..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

echo "🚀 Running new container..."
docker run -d \
  --name "$CONTAINER_NAME" \
  -p "$PORT:8501" \
  "$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"

echo "✅ Deployed $CONTAINER_NAME on port $PORT"
