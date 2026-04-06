#!/bin/bash

# P Λ R Λ D I T I - Google Cloud Run Deployment Script
# This script automates the build and deployment process to ensure a "Live Preview" URL for submission.

# Configuration
PROJECT_ID="[YOUR_GCP_PROJECT_ID]"
SERVICE_NAME="paraditi-mobility-platform"
REGION="us-central1"
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

echo "🚀 Starting Deployment for P Λ R Λ D I T I..."

# 1. Enable Google Cloud Services (Requirement)
echo "📦 Enabling required Google Cloud APIs..."
gcloud services enable run.googleapis.com containerregistry.googleapis.com

# 2. Build Docker Image locally or via Cloud Build
echo "🏗️ Building Docker Image [$IMAGE_TAG]..."
docker build -t $IMAGE_TAG .

# 3. Push to Google Container Registry
echo "📤 Pushing Image to GCR..."
docker push $IMAGE_TAG

# 4. Deploy to Cloud Run
echo "⚡ Deploying to Cloud Run [$SERVICE_NAME]..."
# --allow-unauthenticated is usually required for hackathon public previews
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 5000 \
    --memory 2Gi \
    --cpu 1 \
    --set-env-vars="FLASK_ENV=production,FLASK_APP=backend.app:create_app()"

echo "✅ SUCCESS: Your Paraditi Platform is now LIVE!"
echo "🔗 Deployment URL: $(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format='value(status.url)')"
echo "--------------------------------------------------------"
echo "👉 Use the URL above for your Hack2Skill submission form!"
