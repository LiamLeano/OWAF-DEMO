import subprocess
import sys

def run_script(script_path):
    """
    Runs a Python script using subprocess.

    Args:
        script_path (str): The path to the Python script.
    
    Raises:
        subprocess.CalledProcessError: If the script returns a non-zero exit status.
    """
    print(f"\nRunning script: {script_path}")
    # Use sys.executable to call the same interpreter that is running this script.
    subprocess.run([sys.executable, script_path], check=True)

def main():
    try:
        # Run the schema creation script.
        run_script("datasets/raw-data/schema/schema.py")

        # Run the dataset processing script.
        run_script("datasets/datasets.py")
        
        # Run the content creation script.
        run_script("content/content.py")
        
        print("All scripts executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running scripts: {e}")

if __name__ == '__main__':
    main()
