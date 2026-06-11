#!/bin/bash
set -e

echo "Updating dependencies..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt

echo "Starting heer Music Bot..."
python3 -m heer
 
