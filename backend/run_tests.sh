#!/bin/bash

# Test runner script for KovaaK's AI Trainer Backend

set -e

echo "🧪 KovaaK's AI Trainer - Test Suite"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-yes}"

# Check if pytest is installed
if ! python -m pytest --version > /dev/null 2>&1; then
    echo -e "${RED}✗ pytest not installed${NC}"
    echo "Installing test dependencies..."
    pip install -r requirements-dev.txt
fi

# Run tests based on type
case "$TEST_TYPE" in
    "unit")
        echo -e "${YELLOW}Running unit tests only...${NC}"
        if [ "$COVERAGE" = "yes" ]; then
            python -m pytest -m unit --cov=app --cov-report=term-missing --cov-report=html -v
        else
            python -m pytest -m unit -v
        fi
        ;;
    "integration")
        echo -e "${YELLOW}Running integration tests only...${NC}"
        if [ "$COVERAGE" = "yes" ]; then
            python -m pytest -m integration --cov=app --cov-report=term-missing --cov-report=html -v
        else
            python -m pytest -m integration -v
        fi
        ;;
    "api")
        echo -e "${YELLOW}Running API tests only...${NC}"
        if [ "$COVERAGE" = "yes" ]; then
            python -m pytest -m api --cov=app --cov-report=term-missing --cov-report=html -v
        else
            python -m pytest -m api -v
        fi
        ;;
    "fast")
        echo -e "${YELLOW}Running fast tests (excluding slow and external)...${NC}"
        if [ "$COVERAGE" = "yes" ]; then
            python -m pytest -m "not slow and not external" --cov=app --cov-report=term-missing --cov-report=html -v
        else
            python -m pytest -m "not slow and not external" -v
        fi
        ;;
    "all")
        echo -e "${YELLOW}Running all tests...${NC}"
        if [ "$COVERAGE" = "yes" ]; then
            python -m pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml -v
        else
            python -m pytest -v
        fi
        ;;
    *)
        echo -e "${RED}✗ Invalid test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: ./run_tests.sh [test_type] [coverage]"
        echo ""
        echo "Test types:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests only"
        echo "  api          - Run API tests only"
        echo "  fast         - Run fast tests (exclude slow/external)"
        echo ""
        echo "Coverage:"
        echo "  yes          - Generate coverage report (default)"
        echo "  no           - Skip coverage"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                  # All tests with coverage"
        echo "  ./run_tests.sh unit             # Unit tests with coverage"
        echo "  ./run_tests.sh integration no   # Integration tests without coverage"
        echo "  ./run_tests.sh fast             # Fast tests with coverage"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"

    if [ "$COVERAGE" = "yes" ]; then
        echo ""
        echo "Coverage report generated:"
        echo "  - Terminal: see above"
        echo "  - HTML: htmlcov/index.html"
        echo "  - XML: coverage.xml"
        echo ""
        echo "To view HTML report:"
        echo "  open htmlcov/index.html"
    fi
else
    echo ""
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
