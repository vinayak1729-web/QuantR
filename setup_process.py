#!/usr/bin/env python3
"""
Automated PyPI Package Upload Script
Usage: python upload_to_pypi.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(message):
    """Print a step message in blue"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {message}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(message):
    """Print success message in green"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Print error message in red"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        print(e.stderr)
        return None

def check_env_file():
    """Check if .env file exists and has required variables"""
    print_step("Checking environment configuration")
    
    if not os.path.exists('.env'):
        print_error(".env file not found!")
        print("\nPlease create a .env file with your PyPI token.")
        print("Example:")
        print("  PYPI_TOKEN=pypi-YOUR_TOKEN_HERE")
        return False
    
    pypi_token = os.getenv('PYPI_TOKEN')
    
    if not pypi_token:
        print_error("PYPI_TOKEN not found in .env file!")
        return False
    
    if not pypi_token.startswith('pypi-'):
        print_error("PYPI_TOKEN should start with 'pypi-'")
        return False
    
    print_success(".env file configured correctly")
    return True

def create_pypirc():
    """Create .pypirc file with credentials from environment"""
    print_step("Creating .pypirc file")
    
    pypi_token = os.getenv('PYPI_TOKEN')
    home_dir = Path.home()
    pypirc_path = home_dir / '.pypirc'
    
    pypirc_content = f"""[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = {pypi_token}
"""
    
    try:
        with open(pypirc_path, 'w') as f:
            f.write(pypirc_content)
        
        # Set appropriate permissions (Unix-like systems)
        if os.name != 'nt':  # Not Windows
            os.chmod(pypirc_path, 0o600)
        
        print_success(f".pypirc created at {pypirc_path}")
        return True
    except Exception as e:
        print_error(f"Failed to create .pypirc: {e}")
        return False

def clean_build_artifacts():
    """Remove old build artifacts"""
    print_step("Cleaning old build artifacts")
    
    dirs_to_remove = ['dist', 'build', '*.egg-info']
    
    for pattern in dirs_to_remove:
        if '*' in pattern:
            # Handle wildcard patterns
            for path in Path('.').glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                    print_success(f"Removed {path}")
        else:
            if os.path.exists(pattern):
                shutil.rmtree(pattern)
                print_success(f"Removed {pattern}")
    
    print_success("Build artifacts cleaned")

def check_dependencies():
    """Check if required tools are installed"""
    print_step("Checking dependencies")
    
    dependencies = {
        'build': 'python -m build',
        'twine': 'twine --version'
    }
    
    missing = []
    
    for dep, command in dependencies.items():
        result = run_command(command, check=False)
        if result and result.returncode == 0:
            print_success(f"{dep} is installed")
        else:
            print_error(f"{dep} is not installed")
            missing.append(dep)
    
    if missing:
        print_warning("\nInstalling missing dependencies...")
        for dep in missing:
            install_cmd = f"pip install {dep}"
            print(f"Running: {install_cmd}")
            result = run_command(install_cmd)
            if result:
                print_success(f"{dep} installed successfully")
    
    return True

def build_package():
    """Build the package distribution"""
    print_step("Building package")
    
    result = run_command("python -m build")
    
    if result and result.returncode == 0:
        print_success("Package built successfully")
        return True
    else:
        print_error("Package build failed")
        return False

def check_package():
    """Check package with twine"""
    print_step("Checking package")
    
    result = run_command("twine check dist/*")
    
    if result and result.returncode == 0:
        print_success("Package checks passed")
        return True
    else:
        print_error("Package check failed")
        return False

def upload_to_pypi():
    """Upload package to PyPI"""
    print_step("Uploading to PyPI")
    
    # Ask for confirmation
    response = input(f"\n{Colors.YELLOW}Ready to upload to PyPI. Continue? (y/n): {Colors.END}")
    
    if response.lower() != 'y':
        print_warning("Upload cancelled by user")
        return False
    
    result = run_command("twine upload dist/*")
    
    if result and result.returncode == 0:
        print_success("Package uploaded successfully!")
        print(f"\n{Colors.GREEN}🎉 Your package is now live on PyPI!{Colors.END}")
        return True
    else:
        print_error("Upload failed")
        return False

def upload_to_test_pypi():
    """Upload package to TestPyPI for testing"""
    print_step("Uploading to TestPyPI")
    
    test_token = os.getenv('TEST_PYPI_TOKEN')
    
    if not test_token:
        print_warning("TEST_PYPI_TOKEN not found. Skipping TestPyPI upload.")
        return True
    
    response = input(f"\n{Colors.YELLOW}Upload to TestPyPI first? (y/n): {Colors.END}")
    
    if response.lower() != 'y':
        return True
    
    result = run_command(
        f"twine upload --repository testpypi dist/* -u __token__ -p {test_token}"
    )
    
    if result and result.returncode == 0:
        print_success("Package uploaded to TestPyPI successfully!")
        print("\nTest installation with:")
        print(f"  pip install --index-url https://test.pypi.org/simple/ QuantResearch")
        return True
    else:
        print_error("TestPyPI upload failed")
        return False

def main():
    """Main execution flow"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  PyPI Package Upload Automation")
    print(f"  QuantResearch by Vinayak Shinde")
    print(f"{'='*60}{Colors.END}\n")
    
    # Step 1: Check environment
    if not check_env_file():
        sys.exit(1)
    
    # Step 2: Create .pypirc
    if not create_pypirc():
        sys.exit(1)
    
    # Step 3: Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Step 4: Clean old builds
    clean_build_artifacts()
    
    # Step 5: Build package
    if not build_package():
        sys.exit(1)
    
    # Step 6: Check package
    if not check_package():
        sys.exit(1)
    
    # Step 7: Optional - Upload to TestPyPI
    upload_to_test_pypi()
    
    # Step 8: Upload to PyPI
    if not upload_to_pypi():
        sys.exit(1)
    
    print(f"\n{Colors.GREEN}{'='*60}")
    print(f"  ✓ All done! Package successfully published.")
    print(f"{'='*60}{Colors.END}\n")
    
    print("Install your package with:")
    print(f"  pip install QuantResearch\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ Upload cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)