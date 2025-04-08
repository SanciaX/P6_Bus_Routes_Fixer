import sys
import subprocess
import os

# Ensure Python version is 3.9 or higher
if sys.version_info < (3, 9):
    sys.exit("Error: Python 3.9 or higher is required. Please install it first.")

# Define venv path
venv_path = ".venv"
python_exe = os.path.join(venv_path, "Scripts", "python.exe") if os.name == "nt" else os.path.join(venv_path, "bin", "python")

# Create virtual environment if it doesn't exist
if not os.path.exists(venv_path):
    print("Creating virtual environment...")
    subprocess.check_call([sys.executable, "-m", "venv", venv_path])
else:
    print("Virtual environment already exists. Skipping creation.")

print("Installing dependencies...")
subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
subprocess.check_call([python_exe, "-m", "pip", "install", "-r", "requirements.txt"])

# Activation instructions
print("\n Setup complete.")
if os.name == "nt":
    print("To activate the environment, run: .venv\\Scripts\\activate")
else:
    print("To activate the environment, run: source .venv/bin/activate")

print("Then run your script with:")
print(f"  {python_exe} user_run_scripts/user_run.py")
