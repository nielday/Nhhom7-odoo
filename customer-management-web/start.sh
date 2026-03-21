#!/bin/bash

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start proxy server
echo "Starting proxy server..."
npm start
