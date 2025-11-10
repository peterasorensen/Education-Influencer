"""
Setup verification script for Educational Video Generation Backend.

Run this script to verify all dependencies and system requirements are properly installed.
"""

import sys
import subprocess
import importlib
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def check_python_version():
    """Check Python version."""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 9:
        print("✓ Python version is compatible (3.9+)")
        return True
    else:
        print("✗ Python 3.9 or higher required")
        return False


def check_command(command, version_flag="--version"):
    """Check if a command-line tool is installed."""
    try:
        result = subprocess.run(
            [command, version_flag],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            version_output = result.stdout.strip().split("\n")[0]
            print(f"✓ {command} is installed: {version_output}")
            return True
        else:
            print(f"✗ {command} failed to run")
            return False
    except FileNotFoundError:
        print(f"✗ {command} not found in PATH")
        return False
    except Exception as e:
        print(f"✗ Error checking {command}: {e}")
        return False


def check_python_package(package_name):
    """Check if a Python package is installed."""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, "__version__", "unknown")
        print(f"✓ {package_name} is installed (version: {version})")
        return True
    except ImportError:
        print(f"✗ {package_name} is not installed")
        return False


def check_env_file():
    """Check if .env file exists and has required variables."""
    print_header("Checking Environment Configuration")
    env_file = Path(".env")

    if not env_file.exists():
        print("✗ .env file not found")
        print("  Run: cp .env.example .env")
        print("  Then edit .env and add your OpenAI API key")
        return False

    content = env_file.read_text()

    if "OPENAI_API_KEY" not in content:
        print("✗ .env file missing OPENAI_API_KEY")
        return False

    if "your_openai_api_key_here" in content:
        print("⚠ .env file exists but OPENAI_API_KEY not configured")
        print("  Edit .env and replace 'your_openai_api_key_here' with your actual API key")
        return False

    print("✓ .env file configured")
    return True


def check_output_directory():
    """Check if output directory exists or can be created."""
    print_header("Checking Output Directory")
    output_dir = Path("./output")

    try:
        output_dir.mkdir(exist_ok=True)
        print(f"✓ Output directory ready: {output_dir.absolute()}")
        return True
    except Exception as e:
        print(f"✗ Cannot create output directory: {e}")
        return False


def main():
    """Run all checks."""
    print("\n" + "=" * 60)
    print(" Educational Video Generation Backend - Setup Verification")
    print("=" * 60)

    all_passed = True

    # Check Python version
    all_passed &= check_python_version()

    # Check system dependencies
    print_header("Checking System Dependencies")
    all_passed &= check_command("ffmpeg")
    all_passed &= check_command("ffprobe")

    # Check Manim
    manim_installed = check_command("manim")
    if not manim_installed:
        print("  Note: Manim is required for video generation")
        print("  Install with: pip install manim")

    # Check LaTeX (required for Manim)
    latex_installed = check_command("latex", "-version")
    if not latex_installed:
        print("  Note: LaTeX is required for Manim text rendering")
        print("  macOS: brew install --cask mactex")
        print("  Ubuntu: sudo apt-get install texlive texlive-latex-extra")

    # Check Python packages
    print_header("Checking Python Packages")
    packages = [
        "fastapi",
        "uvicorn",
        "openai",
        "pydub",
        "manim",
        "websockets",
        "pydantic",
    ]

    for package in packages:
        package_installed = check_python_package(package)
        if not package_installed:
            all_passed = False

    # Check environment configuration
    all_passed &= check_env_file()

    # Check output directory
    check_output_directory()

    # Summary
    print_header("Summary")
    if all_passed:
        print("✓ All checks passed! The backend is ready to run.")
        print("\nTo start the server, run:")
        print("  python main.py")
        print("\nAPI documentation will be available at:")
        print("  http://localhost:8000/docs")
    else:
        print("✗ Some checks failed. Please install missing dependencies.")
        print("\nTo install Python packages:")
        print("  pip install -r requirements.txt")
        print("\nTo install system dependencies:")
        print("  See README.md for installation instructions")

    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
