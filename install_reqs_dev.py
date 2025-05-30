import subprocess
import sys


def install_package(package: str) -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


if __name__ == "__main__":
    try:
        with open("requirements-dev.txt", encoding="utf-8") as f:
            for current_line in f:
                line_content = current_line.strip()
                if line_content and not line_content.startswith("#"):
                    print(f"Installing {line_content}...")
                    install_package(line_content)
        print("All dev packages installed successfully.")
    except FileNotFoundError:
        print("Error: requirements-dev.txt not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
