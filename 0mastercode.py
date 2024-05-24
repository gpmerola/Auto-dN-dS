import subprocess
import sys
import time

def run_script(script_filename):
    python_cmds = ['python', 'python3']
    script_path = f'scripts/{script_filename}'

    for python_cmd in python_cmds:
        try:
            start_time = time.time()
            result = subprocess.run([python_cmd, script_path], check=True)
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Script '{script_filename}' took {elapsed_time:.2f} seconds to execute using {python_cmd}.")
            break  # Exit the loop if the script runs successfully
        except subprocess.CalledProcessError:
            print(f"Failed to run script with {python_cmd}. Trying the next option.")
        except FileNotFoundError:
            print(f"{python_cmd} not found. Trying the next option.")

def ask_user():
    scripts = {
        "1": "1list.py",
        "2": "2CDS_fetcher.py",
        "3": "3align.py",
        "4": "4qualityMOS.py"
    }
    print("Select the scripts you want to run:")
    for number, filename in scripts.items():
        print(f"{number}: {filename}")
    print("Enter 'all' to run all scripts.")
    
    choice = input("Enter your choice (e.g., '1, 2' or all): ").strip().lower()
    if choice == 'all':
        return list(scripts.values())
    else:
        selected_scripts = []
        for number in choice.split(','):
            number = number.strip()
            if number in scripts:
                selected_scripts.append(scripts[number])
            else:
                print(f"Invalid selection: {number}")
        return selected_scripts

def main():
    scripts_to_run = ask_user()
    for script_filename in scripts_to_run:
        run_script(script_filename)

if __name__ == "__main__":
    main()
