import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    try:
        with open("requirements-dev.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    print(f"Installing {line}...")
                    install_package(line)
        print("All dev packages installed successfully.")
    except FileNotFoundError:
        print("Error: requirements-dev.txt not found.")
    except Exception as e:
        print(f"An error occurred: {e}") 