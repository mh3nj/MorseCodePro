#!/usr/bin/env python3
"""
Morse Code Pro - Universal Python Installer
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
import venv
from pathlib import Path

class MorseCodeInstaller:
    def __init__(self):
        self.project_name = "MorseCodePro"
        self.repo_url = "https://github.com/mh3nj/MorseCodePro.git"
        self.python_min_version = (3, 11)
        self.colors = self._init_colors()
        
    def _init_colors(self):
        """Initialize terminal colors based on platform"""
        if platform.system() == "Windows":
            return {
                'RED': '', 'GREEN': '', 'YELLOW': '', 'BLUE': '', 
                'CYAN': '', 'NC': ''
            }
        else:
            return {
                'RED': '\033[0;31m',
                'GREEN': '\033[0;32m',
                'YELLOW': '\033[1;33m',
                'BLUE': '\033[0;34m',
                'CYAN': '\033[0;36m',
                'NC': '\033[0m'
            }
    
    def print_status(self, msg, level="INFO"):
        """Print colored status messages"""
        colors = {
            "INFO": self.colors['BLUE'],
            "OK": self.colors['GREEN'],
            "ERROR": self.colors['RED'],
            "WARN": self.colors['YELLOW']
        }
        prefix = colors.get(level, self.colors['CYAN'])
        print(f"{prefix}[{level}]{self.colors['NC']} {msg}")
    
    def check_python(self):
        """Check Python version"""
        version = sys.version_info
        if version.major < self.python_min_version[0] or \
           (version.major == self.python_min_version[0] and 
            version.minor < self.python_min_version[1]):
            self.print_status(
                f"Python {self.python_min_version[0]}.{self.python_min_version[1]}+ required. "
                f"Found: {version.major}.{version.minor}",
                "ERROR"
            )
            return False
        self.print_status(f"Python {version.major}.{version.minor} found", "OK")
        return True
    
    def check_git(self):
        """Check if Git is available"""
        try:
            result = subprocess.run(['git', '--version'], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                self.print_status(f"Git found: {result.stdout.strip()}", "OK")
                return True
        except FileNotFoundError:
            pass
        self.print_status("Git not found. Will use existing files only.", "WARN")
        return False
    
    def clone_or_update(self):
        """Clone repository or update existing"""
        project_path = Path.cwd() / self.project_name
        
        if project_path.exists():
            self.print_status(f"Found existing {self.project_name} directory", "INFO")
            if self.check_git():
                os.chdir(project_path)
                result = subprocess.run(['git', 'pull', 'origin', 'main'],
                                       capture_output=True)
                if result.returncode == 0:
                    self.print_status("Successfully updated", "OK")
                else:
                    self.print_status("Git pull failed, using existing files", "WARN")
            return project_path
        else:
            if self.check_git():
                self.print_status("Cloning repository...", "INFO")
                result = subprocess.run(['git', 'clone', self.repo_url])
                if result.returncode == 0:
                    self.print_status("Repository cloned successfully", "OK")
                    return project_path
            self.print_status("Please download the source code manually", "ERROR")
            return None
    
    def create_venv(self, project_path):
        """Create virtual environment"""
        venv_path = project_path / ".venv"
        
        if venv_path.exists():
            self.print_status("Virtual environment already exists", "OK")
            return venv_path
        
        self.print_status("Creating virtual environment...", "INFO")
        try:
            venv.create(venv_path, with_pip=True)
            self.print_status("Virtual environment created", "OK")
            return venv_path
        except Exception as e:
            self.print_status(f"Failed to create venv: {e}", "ERROR")
            return None
    
    def get_pip_path(self, venv_path):
        """Get pip executable path based on platform"""
        if platform.system() == "Windows":
            return venv_path / "Scripts" / "pip.exe"
        else:
            return venv_path / "bin" / "pip"
    
    def get_python_path(self, venv_path):
        """Get python executable path based on platform"""
        if platform.system() == "Windows":
            return venv_path / "Scripts" / "python.exe"
        else:
            return venv_path / "bin" / "python"
    
    def install_dependencies(self, venv_path, project_path):
        """Install Python dependencies"""
        requirements = project_path / "requirements.txt"
        
        if not requirements.exists():
            self.print_status("requirements.txt not found!", "ERROR")
            return False
        
        pip = self.get_pip_path(venv_path)
        
        # Upgrade pip
        self.print_status("Upgrading pip...", "INFO")
        subprocess.run([str(pip), 'install', '--upgrade', 'pip'], 
                      capture_output=True)
        
        # Install dependencies
        self.print_status("Installing dependencies...", "INFO")
        result = subprocess.run([str(pip), 'install', '-r', str(requirements)],
                               capture_output=True)
        
        if result.returncode == 0:
            self.print_status("All dependencies installed", "OK")
            return True
        else:
            self.print_status("Some dependencies failed. Trying core packages...", "WARN")
            # Install core packages one by one
            core_packages = ['customtkinter', 'numpy', 'scipy', 
                           'sounddevice', 'pyttsx3']
            for package in core_packages:
                subprocess.run([str(pip), 'install', package], capture_output=True)
            return True
    
    def launch_app(self, venv_path, project_path):
        """Launch the Morse Code Pro application"""
        python = self.get_python_path(venv_path)
        main_script = project_path / "main.py"
        
        if not main_script.exists():
            self.print_status("main.py not found!", "ERROR")
            return False
        
        self.print_status("Launching Morse Code Pro...", "INFO")
        print("\n" + "="*50)
        print("     Morse Code Pro is Starting...")
        print("="*50 + "\n")
        
        # Launch the app
        subprocess.run([str(python), str(main_script)])
        return True
    
    def run(self):
        """Main installation flow"""
        print("\n" + "="*50)
        print("     Morse Code Pro Installer v1.5")
        print("     Professional Morse Code Suite")
        print("="*50 + "\n")
        
        # Check Python
        if not self.check_python():
            return 1
        
        # Clone or update repository
        project_path = self.clone_or_update()
        if not project_path:
            return 1
        
        # Create virtual environment
        venv_path = self.create_venv(project_path)
        if not venv_path:
            return 1
        
        # Install dependencies
        os.chdir(project_path)
        if not self.install_dependencies(venv_path, project_path):
            return 1
        
        # Launch the app
        self.launch_app(venv_path, project_path)
        
        print("\n" + "="*50)
        print("     Thanks for using Morse Code Pro!")
        print("="*50)
        
        return 0

if __name__ == "__main__":
    installer = MorseCodeInstaller()
    sys.exit(installer.run())