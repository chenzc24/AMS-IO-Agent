#!/bin/bash
# Add local node to PATH for this script execution
export PATH=$HOME/local/node/bin:$PATH

# Navigate to frontend dir
# Assuming this script is in AMS-IO-Agent/
cd "$(dirname "$0")/../anthropic-gui"

echo "Using Node: $(which node)"

# Install dependencies only when needed to avoid long startup delays.
if [ "${FORCE_NPM_INSTALL:-0}" = "1" ] || [ ! -d "node_modules" ]; then
	echo "Installing dependencies (this may take a few minutes)..."
	npm install --legacy-peer-deps
else
	echo "Dependencies already installed, skipping npm install."
	echo "Set FORCE_NPM_INSTALL=1 to reinstall dependencies."
fi

echo "Starting Application..."
# Force host to 0.0.0.0 to fix binding issues, ignore system HOST variable
export HOST=0.0.0.0
export BROWSER=none

echo "Frontend dev server target: http://localhost:3000"
echo "If running on a remote machine, open local tunnel first:"
echo "  ssh -L 3000:127.0.0.1:3000 <user>@<server>"
npm start
