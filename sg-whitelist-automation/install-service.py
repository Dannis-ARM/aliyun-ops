# Python script to create a batch file for the Go program in the user's Startup folder

import sys
from pathlib import Path
import os # Keep os for os.environ.get

def create_startup_script():
    # Define variables
    script_dir = Path(__file__).resolve().parent
    go_program_path = (
        script_dir / "dist" / "sg-whitelist-automation.exe"
    )
    
    # Get Startup folder path using standard environment variables
    # os.environ.get('APPDATA') returns a string, so convert to Path object
    appdata_path = os.environ.get('APPDATA')
    if appdata_path is None:
        print("Error: APPDATA environment variable not found. Cannot determine Startup folder.")
        sys.exit(1)
    startup_folder = (
        Path(appdata_path)
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
    )
    
    # Ensure the Startup folder exists
    if not startup_folder.exists():
        try:
            startup_folder.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Error creating Startup folder: {e}")
            sys.exit(1)

    batch_file_path = startup_folder / "sg-whitelist-automation.bat"

    # Check if the Go executable exists
    if not go_program_path.exists():
        print(
            f"Error: Go executable not found at {go_program_path}. "
            "Please compile the Go program first."
        )
        sys.exit(1)

    print("Creating batch file in Startup folder...")

    try:
        # Create the content for the batch file
        batch_content = f'@echo off\nstart "" "{go_program_path}"\nexit\n'
        
        with open(batch_file_path, 'w') as f:
            f.write(batch_content)
            
        print(
            f"Batch file created at {batch_file_path}. "
            "The program will run automatically when you log in."
        )
        print(
            "Note: This method creates a batch file to start the program, "
            "as direct .lnk creation with specific properties requires external libraries."
        )
    except Exception as e:
        print(f"Error creating batch file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_startup_script()
