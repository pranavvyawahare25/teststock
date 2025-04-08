#!/usr/bin/env bash
# This script ensures Tailwind CSS is installed and configured properly

# Exit on error
set -e

echo "Installing dependencies..."
npm install

# Ensure Tailwind CSS is installed
echo "Ensuring Tailwind CSS is installed..."
npm install tailwindcss@latest postcss@latest autoprefixer@latest --save

# Generate Prisma client
echo "Generating Prisma client..."
npx prisma generate

# Build the application
echo "Building the application..."
npm run build

echo "Build completed successfully!" 