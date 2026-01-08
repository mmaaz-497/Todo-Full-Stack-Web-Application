#!/bin/bash

echo "🧹 Cleaning up old Minikube installation..."

# Stop any running minikube instance
echo "Stopping Minikube (if running)..."
minikube stop 2>/dev/null || true

# Delete the entire minikube cluster
echo "Deleting Minikube cluster..."
minikube delete --all --purge

# Clean up minikube directories
echo "Cleaning up Minikube directories..."
rm -rf ~/.minikube
rm -rf ~/.kube

# Verify Docker is accessible
echo "Verifying Docker access..."
docker ps

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "🚀 Now starting fresh Minikube cluster..."
echo ""

# Start fresh Minikube cluster
minikube start --cpus=2 --memory=4096 --driver=docker

echo ""
echo "✅ Minikube started successfully!"
echo ""

# Verify status
minikube status

echo ""
echo "🎉 You can now continue with the deployment!"
