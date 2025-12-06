#!/bin/bash

# Forensic Agent Test Runner

set -e

echo "=================================="
echo "Forensic Agent Test Suite"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "=================================="
echo "Running Unit Tests"
echo "=================================="
pytest tests/ -v -m "not skipif" --ignore=tests/test_integration.py

echo ""
echo "=================================="
echo "Test Summary"
echo "=================================="
echo "Unit tests completed."
echo ""
echo "To run integration tests (requires ANTHROPIC_API_KEY):"
echo "  export ANTHROPIC_API_KEY='your_key_here'"
echo "  pytest tests/test_integration.py::TestLiveIntegration -v"
echo ""
echo "To run all tests with coverage:"
echo "  pytest tests/ -v --cov=app --cov-report=html"
echo "  open htmlcov/index.html"
