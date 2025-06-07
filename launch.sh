#!/bin/bash
# Unix/Linux launcher script for the FastAPI + Next.js Dashboard System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
log() {
  local level=$1
  shift
  case $level in
  ERROR) echo -e "${RED}[ERROR]${NC} $*" ;;
  SUCCESS) echo -e "${GREEN}[SUCCESS]${NC} $*" ;;
  WARNING) echo -e "${YELLOW}[WARNING]${NC} $*" ;;
  INFO) echo -e "${BLUE}[INFO]${NC} $*" ;;
  *) echo "$*" ;;
  esac
}

# Check if Python is available
check_python() {
  if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
  elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
  else
    log ERROR "Python not found. Please install Python 3.8 or higher."
    exit 1
  fi

  # Check Python version
  PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
  log INFO "Using Python $PYTHON_VERSION"
}

# Make launcher.py executable and run it
main() {
  log INFO "🚀 Unified Backend & Frontend Launcher"

  # Check for Python
  check_python

  # Make launcher.py executable
  chmod +x launcher.py

  # Run the Python launcher with all arguments
  $PYTHON_CMD launcher.py "$@"
}

# Run main function with all script arguments
main "$@"
