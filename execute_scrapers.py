# These must be installed
# pip install sqlalchemy
# pip install connectorx
# pip install pyarrow
import os
import re
import subprocess
import threading




# List of scripts to run
scripts_to_run = [x for x in os.listdir("scrapers") if re.match("scraper_.*py",x)]
scripts_to_run = ['scrapers/'+x for x in scripts_to_run if x=='scraper_NO_nmbu.py']



# Function to run a script and display its output
def run_script(script):
    process = subprocess.Popen(
        ["python", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,  # Ensures the output is in text mode
        bufsize=1,  # Line-buffered output
    )

    # Read stdout and stderr in real-time
    def read_output(pipe, output_type):
        for line in iter(pipe.readline, ''):
            if line:
                print(f"[{script} - {output_type}] {line.strip()}")
        pipe.close()

    # Start threads to read stdout and stderr
    stdout_thread = threading.Thread(target=read_output, args=(process.stdout, "stdout"))
    stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "stderr"))

    stdout_thread.start()
    stderr_thread.start()

    # Wait for the process to complete
    process.wait()

    # Wait for threads to finish reading
    stdout_thread.join()
    stderr_thread.join()

    print(f"[{script}] Execution completed with return code: {process.returncode}")

# Run scripts in parallel
threads = []
for script in scripts_to_run:
    thread = threading.Thread(target=run_script, args=(script,))
    thread.start()
    threads.append(thread)

# Wait for all threads to complete
for thread in threads:
    thread.join()