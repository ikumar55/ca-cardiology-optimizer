#!/bin/sh

# Docker entrypoint script for Cardiology Care Optimization System

set -e

# Default to running the dashboard if no command is provided
if [ -z "$1" ]; then
    set -- "run-dashboard"
fi

# Execute the given command
case "$1" in
    run-dashboard)
        echo "Starting Streamlit dashboard..."
        streamlit run src/visualization/dashboard.py
        ;;
    run-notebook)
        echo "Starting Jupyter Lab..."
        jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
        ;;
    train-model)
        echo "Starting model training..."
        python src/models/train.py "${@:2}"
        ;;
    run-tests)
        echo "Running tests..."
        pytest
        ;;
    bash)
        # Drop into a shell
        exec /bin/bash
        ;;
    *)
        # Execute any other command
        exec "$@"
        ;;
esac 