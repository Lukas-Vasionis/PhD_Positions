import os
import regex as re
import subprocess

# List of scripts to run
scripts_to_run = [x for x in os.listdir("scrapers") if re.match("scraper_.*py", x)]
scripts_to_run = ['scrapers/' + x for x in scripts_to_run]


def execute_script(script_path):
    attempts = 3  # Maximum number of attempts
    for attempt in range(1, attempts + 1):
        print(f"Attempt: {attempt} for {script_path}")

        # Execute the script and capture the output
        process = subprocess.Popen(
            ['python', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Read the output and error streams
        stdout, stderr = process.communicate()

        # Check if there's an error
        if process.returncode == 0:
            # Successful execution, return the output
            return script_path, stdout, stderr
        else:
            print(f"\tError from {script_path} (Attempt {attempt}):\n\t{stderr.replace('\n', '\n\t')}")
            if "OperationalError" in stderr or attempt < attempts:
                print(f"Retrying {script_path} (Attempt {attempt + 1}/{attempts})...")
            else:
                # Maximum attempts reached, return the error
                return script_path, stdout, stderr


def run_scripts(scripts):
    for script in scripts:
        script_path, stdout, stderr = execute_script(script)

        if stdout:
            print(f"Output from {script_path}:\n{stdout}")
        if stderr:
            print(f"Final Error from {script_path}:\n{stderr.replace('\n', '\n\t')}")


# Run the scripts sequentially
run_scripts(scripts_to_run)
