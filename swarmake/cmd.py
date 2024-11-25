import subprocess
import sys
import time
from datetime import datetime
from itertools import cycle

from swarmake.logger import setup_logging, LOGGER
logging = LOGGER.bind(context=__name__)  # Bind initial context (__name__)


def execute(command, tag=None, directory=None):
    """
    Just execute the specified command, and return the return code.
    """
    executed, stdout, stderr = execute_and_output(command, tag, directory)
    return executed

def execute_and_output(command, tag=None, directory=None):
    """
    Just execute the specified command, and return the return code.
    """
    # Bind the tag to the logger context
    logger = logging.bind(tag=tag)

    if command:
        if directory:
            command = f"cd {directory} && {command}"

        # Log the command execution start
        logger.debug(f"Executing command: \n\n\t{command}\n\n")

        # Start timer
        start_time = datetime.now()

        # Capture output and wait for the process to finish
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        elapsed_time = round((datetime.now() - start_time).total_seconds(), 3)

        if process.returncode != 0:
            logger.error(f"Command failed for tag {tag}", error=stderr.decode())
            return False, stdout.decode(), stderr.decode()
        else:
            logger.debug(f"Completed with status {process.returncode} in {elapsed_time} s")

        return process.returncode == 0, stdout.decode(), stderr.decode()
    else:
        logger.debug(f"No command specified")
        return False, "", ""


def execute_pretty(command, tag=None, directory=None, force_show_output=False, is_interactive=False):
    """
    Execute the specified command for the project, displaying a spinner and elapsed time.

    Display a spinner and a timer for the command execution only when stderr is redirected.
    """
    # Bind the tag to the logger context
    logger = logging.bind(project=tag)

    # Check if stderr is interactive (not redirected)
     # FIXME the passed parameter is_interactive is not having the expected effect
    is_interactive = is_interactive or sys.stderr.isatty()

    is_ok = False

    if command:
        if directory:
            command = f"cd {directory} && {command}"

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
                    sys.stdout.write(f"\r{spinner} Running {tag}... Time elapsed: {str(elapsed_time).split('.')[0]} ")
                    sys.stdout.flush()
                time.sleep(0.1)  # Pause to simulate spinner speed

            # Capture output and wait for the process to finish
            stdout, stderr = process.communicate()

            elapsed_time = round(elapsed_time.total_seconds(), 3)

            # If we're in interactive mode, we don't need to show stdout/stderr, it goes directly to the terminal.
            if is_interactive:
                if process.returncode != 0:
                    logger.error(f"Command failed")
                    raise RuntimeError(f"Command failed {tag}")
                else:
                    is_ok = True
                    logger.debug(f"Completed ok in {elapsed_time} s")
            else:
                # # Capture output and wait for the process to finish
                # stdout, stderr = process.communicate()

                if process.returncode != 0:
                    sys.stdout.write("\r \n")  # Clean up the spinner line
                    logger.error(f"Command failed", error=stderr.decode())
                    raise RuntimeError(f"Command failed {tag}")
                else:
                    is_ok = True
                    sys.stdout.write(f"\r✔ Completed             \n") # extra spaces to overwrite spinner line
                    logger.debug(f"Completed ok in {elapsed_time} s")
                    if force_show_output:
                        sys.stdout.write(stdout.decode())  # Output the command's stdout
        finally:
            if not is_interactive:
                sys.stdout.write("\n")  # Ensure newline after command execution ends
    else:
        logger.debug(f"No command specified")

    return is_ok
