#!/bin/bash

# Morse Code Pro - Cross-platform Launcher for Linux/macOS
# Version: 2.0
# Author: Mohsen Jafari

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Store starting directory
START_DIR=$(pwd)

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_header() {
    echo -e "${CYAN}"
    echo "      Morse Code Pro v1.5 Setup"
    echo "    Professional Morse Code Suite"
    echo -e "${NC}"
}

# Main execution
print_header

# Check Python installation
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    echo "Please install Python 3.11+ from https://python.org"
    echo "Or use your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3.11 python3-pip python3-venv"
    echo "  Fedora: sudo dnf install python3.11 python3-pip"
    echo "  macOS: brew install python@3.11"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]); then
    print_error "Python 3.11+ is required. Detected: $PYTHON_VERSION"
    exit 1
fi

print_success "Python found: $PYTHON_VERSION"
echo ""

# Check for Git (optional)
if command -v git &> /dev/null; then
    print_success "Git found: $(git --version)"
    GIT_AVAILABLE=1
else
    print_warning "Git not found. Will use existing files only."
    GIT_AVAILABLE=0
fi
echo ""

# Clone or update repository
if [ -d "MorseCodePro" ]; then
    cd MorseCodePro
    print_status "Found existing MorseCodePro directory"
    
    if [ $GIT_AVAILABLE -eq 1 ]; then
        print_status "Pulling latest changes..."
        git pull origin main 2>/dev/null
        if [ $? -eq 0 ]; then
            print_success "Successfully updated to latest version"
        else
            print_warning "Git pull failed, continuing with existing files"
        fi
    fi
else
    if [ $GIT_AVAILABLE -eq 1 ]; then
        print_status "Cloning repository..."
        git clone https://github.com/mh3nj/MorseCodePro.git
        if [ $? -ne 0 ]; then
            print_error "Failed to clone repository!"
            exit 1
        fi
        print_success "Repository cloned successfully"
        cd MorseCodePro
    else
        print_error "MorseCodePro directory not found and Git not available!"
        echo "Please download the source code manually from GitHub"
        exit 1
    fi
fi

echo ""

# Setup virtual environment
print_status "Setting up Python virtual environment..."

if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment!"
        cd "$START_DIR"
        exit 1
    fi
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment!"
    cd "$START_DIR"
    exit 1
fi
print_success "Virtual environment activated"
echo ""

# Check for requirements.txt
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found!"
    cd "$START_DIR"
    exit 1
fi

# Install/upgrade dependencies
print_status "Installing/updating dependencies..."
echo "This may take a few minutes on first run..."
echo ""

# Upgrade pip
python -m pip install --upgrade pip

# Install core dependencies
print_status "Installing core dependencies..."
pip install customtkinter numpy scipy 2>/dev/null

# Install audio dependencies
print_status "Installing audio dependencies..."
pip install sounddevice soundfile simpleaudio pyttsx3 2>/dev/null

# Install optional dependencies (continue if fail)
print_status "Installing optional dependencies..."
pip install matplotlib pydub keyboard 2>/dev/null

if [ $? -ne 0 ]; then
    print_warning "Some optional dependencies failed to install"
    echo "The app will still work with core features"
else
    print_success "All dependencies installed successfully"
fi

echo ""
print_success "Setup complete!"
echo ""

# Check for audio libraries on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_status "Checking audio libraries for Linux..."
    if ! command -v portaudio &> /dev/null; then
        print_warning "PortAudio not found. For better microphone support, install:"
        echo "  Ubuntu/Debian: sudo apt install portaudio19-dev python3-pyaudio"
        echo "  Fedora: sudo dnf install portaudio-devel"
    fi
    echo ""
fi

# Launch the application
print_header
print_status "Launching Morse Code Pro..."
echo ""

python main.py

# Check if app exited normally
if [ $? -eq 0 ]; then
    print_success "Thanks for using Morse Code Pro!"
else
    print_error "Application exited with errors"
fi

echo ""
echo "You can re-run this script anytime to update and launch the app."
echo ""

# Return to original directory
cd "$START_DIR"