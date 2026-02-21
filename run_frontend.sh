#!/bin/bash
# Add local node to PATH for this script execution
export PATH=$HOME/local/node/bin:$PATH

# Navigate to frontend dir
# Assuming this script is in AMS-IO-Agent/
cd "$(dirname "$0")/../anthropic-gui"

echo "Using Node: $(which node)"
echo "Installing dependencies (this may take a few minutes)..."
npm install --legacy-peer-deps

echo "Starting Application..."
# Force host to 0.0.0.0 to fix binding issues, ignore system HOST variable
export HOST=0.0.0.0
export BROWSER=none
npm start
