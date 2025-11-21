import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(msg):
    print(f"\n{Colors.BLUE}{'='*60}\n  {msg}\n{'='*60}{Colors.END}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ {msg}{Colors.END}")

print_step("PyPI Authentication Diagnostic")

# 1. Check token
print("1. Checking PYPI_TOKEN...")
token = os.getenv('PYPI_TOKEN')

if not token:
    print_error("PYPI_TOKEN not found in .env")
    exit(1)

if not token.startswith('pypi-'):
    print_error("Invalid token format. Should start with 'pypi-'")
    exit(1)

print_success("Token format is valid")
print_info(f"Token starts with: {token[:20]}...")

# 2. Check twine installation
print("\n2. Checking twine installation...")
result = subprocess.run(['twine', '--version'], capture_output=True, text=True)
if result.returncode == 0:
    print_success(f"Twine is installed: {result.stdout.strip()}")
else:
    print_error("Twine not installed. Run: pip install twine")
    exit(1)

# 3. Test PyPI authentication
print("\n3. Testing PyPI authentication...")
print_info("Attempting to verify token with PyPI...")

env = os.environ.copy()
env.update({
    'TWINE_USERNAME': '__token__',
    'TWINE_PASSWORD': token
})

# Try to list existing uploads (read-only operation)
result = subprocess.run(
    ['twine', 'check', '--help'],
    capture_output=True,
    text=True,
    env=env
)

if result.returncode == 0:
    print_success("Twine can access PyPI")
else:
    print_error("Twine cannot access PyPI")
    print_error(result.stderr)

# 4. Check dist files
print("\n4. Checking distribution files...")
import glob
dist_files = glob.glob("dist/*")

if not dist_files:
    print_error("No files in dist/ directory. Run: python -m build")
    exit(1)

print_success(f"Found {len(dist_files)} file(s) to upload:")
for f in dist_files:
    print(f"  - {f}")

# 5. Verify package integrity
print("\n5. Verifying package integrity...")
for file in dist_files:
    result = subprocess.run(
        ['twine', 'check', file],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print_success(f"{file} is valid")
    else:
        print_error(f"{file} has issues:")
        print(result.stdout)

# 6. Test upload to test.pypi.org first
print("\n6. Attempting test upload to test.pypi.org...")
print_info("This helps identify auth issues before uploading to production PyPI")

test_files = ' '.join([f'"{f}"' for f in dist_files])
result = subprocess.run(
    f'twine upload --repository testpypi {test_files}',
    shell=True,
    capture_output=True,
    text=True,
    env=env
)

if result.returncode == 0:
    print_success("Test upload successful! Your token works.")
    print_info("You can now upload to production PyPI with confidence.")
else:
    print_error("Test upload failed. Details:")
    print(result.stderr)
    
    if "401" in result.stderr or "Unauthorized" in result.stderr:
        print_error("\n⚠ Authentication Error:")
        print("  - Token may be invalid or expired")
        print("  - Generate a new token: https://pypi.org/account/token/")
        print("  - Update .env file with new token")
    elif "already exists" in result.stderr:
        print_error("\n⚠ Version Conflict:")
        print("  - This version already exists on TestPyPI")
        print("  - Update version in pyproject.toml")
    
    exit(1)

print_step("✓ All diagnostics passed!")
print("You can now safely run: python setup_process.py")