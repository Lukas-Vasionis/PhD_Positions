
import os
import regex as re
import concurrent.futures
import subprocess

# List of scripts to run
scripts_to_run = [x for x in os.listdir("scrapers") if re.match("scraper_.*py", x)]
scripts_to_run = ['scrapers/' + x for x in scripts_to_run]


def execute_script(script_path):
    # Execute the script and capture the output
    process = subprocess.Popen(
        ['python', script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Read the output and error streams line by line
    stdout, stderr = process.communicate()

    # Return the script path and output for tracking
    return script_path, stdout, stderr


def run_scripts_in_parallel(scripts):
    # Get the number of available cores
    max_workers = os.cpu_count()

    # Use ProcessPoolExecutor to run scripts in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit each script for execution
        futures = {executor.submit(execute_script, script): script for script in scripts}

        # Wait for all scripts to complete
        for future in concurrent.futures.as_completed(futures):
            script_path = futures[future]
            try:
                # Get the result of the future
                script, stdout, stderr = future.result()

                # Print the output with the script name
                if stdout:
                    print(f"Output from {script}:\n{stdout}")
                if stderr:
                    print(f"Error from {script}:\n{stderr}")

            except Exception as e:
                print(f"An error occurred in script {script_path}: {e}")


# Run the scripts in parallel
run_scripts_in_parallel(scripts_to_run)
