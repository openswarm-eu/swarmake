# import logging
import subprocess
import sys
import time
from datetime import datetime
from itertools import cycle

# import log
from openswarm.logger import setup_logging, LOGGER
logging = LOGGER.bind(context=__name__)  # Bind initial context (__name__)

def execute_command(command, project_name):
    """
    Execute the specified command for the project.

    Display a spinner and a timer for the command execution only when stderr is redirected.
    """
    # Bind the project_name to the logger context
    logger = logging.bind(project=project_name)

    # Check if stderr is interactive (not redirected)
    is_interactive = sys.stderr.isatty()

    if command:
        # Log the command execution start
        logger.debug(f"Executing command: \n\n\t{command}\n\n")

        # Start timer
        start_time = datetime.now()

        if is_interactive:
            # In interactive mode, let stdout/stderr be passed directly to the terminal
            process = subprocess.Popen(command, shell=True)
        else:
            # In non-interactive mode, capture stdout and stderr
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        spinner_cycle = cycle(['|', '/', '-', '\\']) if not is_interactive else None
        try:
            # Display a spinner and elapsed time while the process runs if not interactive
            while process.poll() is None:
                # Calculate elapsed time
                elapsed_time = datetime.now() - start_time
                if not is_interactive:
                    # Update spinner and time display only if stderr is redirected
                    spinner = next(spinner_cycle)
                    sys.stdout.write(f"\r{spinner} Running {project_name}... Time elapsed: {str(elapsed_time).split('.')[0]} ")
                    sys.stdout.flush()
                time.sleep(0.1)  # Pause to simulate spinner speed

            # If we're in interactive mode, we don't need to capture stdout/stderr, it goes directly to the terminal.
            if is_interactive:
                # Wait for the process to finish without capturing output (since it's already printed in real-time)
                process.communicate()

                if process.returncode != 0:
                    logger.error(f"Command failed")
                    raise RuntimeError(f"Command failed for project {project_name}")
                else:
                    logger.debug(f"Command completed successfully")
            else:
                # Capture output and wait for the process to finish
                stdout, stderr = process.communicate()

                if process.returncode != 0:
                    sys.stdout.write("\r \n")  # Clean up the spinner line
                    logger.error(f"Command failed", error=stderr.decode())
                    raise RuntimeError(f"Command failed for project {project_name}")
                else:
                    sys.stdout.write(f"\r✔ Command completed successfully for project {project_name} in {round(elapsed_time.total_seconds(), 3)} s\n")
                    logger.debug(f"Command completed successfully")
                    sys.stdout.write(stdout.decode())  # Output the command's stdout

        finally:
            if not is_interactive:
                sys.stdout.write("\n")  # Ensure newline after command execution ends
    else:
        logger.debug(f"No command specified")
