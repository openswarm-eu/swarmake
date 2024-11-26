#!/usr/bin/env python

import os
import subprocess
import click
import shutil
import time

from swarmake.logger import setup_logging, LOGGER
logging = LOGGER.bind(context=__name__)

from swarmake import cmd
from swarmake.config import config

def load_project_config(project_name):
    logging.debug(f"Loading project configuration", project_name=project_name)
    
    # Access the project from the config's project dictionary
    if project_name not in config.projects:
        raise ValueError(f"Project '{project_name}' not found in configuration.")

    # Return the project directly
    return config.projects[project_name]

def clone_repository(url, destination):
    if not os.path.exists(destination):
        logging.info(f"Cloning repository", url=url, destination=destination)
        subprocess.run(["git", "clone", url, destination])
    else:
        logging.info(f"Repository already cloned.", url=url, destination=destination)

def clean_build_dir(project_name=None):
    """Clean the build directory for the specified project."""
    build_dir = config.core.build_dir
    if project_name:
        build_dir = f"{build_dir}/{project_name}"
        logging.info(f"Cleaning build directory for project", project_name=project_name, build_dir=build_dir)
    else:
        logging.info(f"Cleaning the full build directory", build_dir=build_dir)
    if os.path.exists(build_dir):
        logging.info(f"Cleaning build directory", build_dir=build_dir)
        shutil.rmtree(build_dir)
    else:
        logging.info(f"Build directory does not exist", build_dir=build_dir)

@click.group()
@click.version_option(package_name="swarmake", message="%(prog)s v%(version)s    Fetch, build, and run the OpenSwarm.")
@click.pass_context
def main(ctx):
    log_level = "info"
    passed_level = os.environ.get("PYTHON_LOG", "").lower()
    if passed_level in ["debug", "info", "warning", "error"]:
        log_level = passed_level
    setup_logging("swarmake.log", log_level, ["console", "file"])


def do_build(project_name, clean_build_first, is_interactive=False):
    print("\n\n================================================================================")
    print("                                 BUILDING")
    print("================================================================================\n\n")

    if clean_build_first:
        clean_build_dir(project_name)

    project = load_project_config(project_name)

    # Clone the repository if necessary
    clone_repository(project.url, project.build_dir)

    # Execute the setup and build commands
    # os.chdir(project.build_dir)
    try:
        if project.setup_cmd:
            logging.info(f"Running setup", project_name=project.name)
            cmd.execute_pretty(project.setup_cmd, project.name, directory=project.build_dir, is_interactive=is_interactive)
        cmd.execute_pretty(project.build_cmd, project.name, directory=project.build_dir, is_interactive=is_interactive)
        if project.list_outputs_cmd:
            logging.info(f"Listing outputs", project_name=project.name)
            cmd.execute_pretty(project.list_outputs_cmd, project.name, directory=project.build_dir, force_show_output=True, is_interactive=is_interactive)
    finally:
        # os.chdir("..")
        pass

@main.command()
@click.option('-c', '--clean-build-first', default=False, is_flag=True, help="Clean the build directory before building")
@click.argument("project_name")
def build(project_name, clean_build_first):
    """Build the specified project"""
    return do_build(project_name, clean_build_first)


@main.command()
@click.option('-c', '--clean-build-first', default=False, is_flag=True, help="Clean the build directory before building")
@click.argument("project_name")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)  # capture extra args after --
def run(project_name, clean_build_first, args):
    """Run the specified project"""
    project = load_project_config(project_name)

    # check if the project is cloned / built
    if not os.path.exists(f"{config.core.build_dir}/{project.name}"):
        raise ValueError(f"Project {project.name} has not been built. Please run 'swarmake build {project.name}' first.")
    
    # Execute the run command
    os.chdir(project.build_dir)
    try:
        full_command = f"{project.run_cmd} {' '.join(args)}"
        cmd.execute_pretty(full_command, project.name)
    finally:
        os.chdir("..")

@main.command()
def list():
    """List available projects."""
    configured_projects = []
    for project_name in config.projects:
        try:
            project = load_project_config(project_name)
            configured_projects.append(project)
        except ValueError as e:
            logging.warning(e)

    configured_project_names = '\n\t'.join([p.name for p in configured_projects])
    logging.info(f"Found {len(configured_projects)} configured projects:\n\n\t{configured_project_names}\n\n")

    all_repos = config.core.repositories
    unconfigured_projects = set(all_repos) - set([p.repo_name for p in configured_projects])
    unconfigured_project_names = '\n\t'.join(unconfigured_projects)
    logging.info(f"Found {len(unconfigured_projects)} unconfigured projects:\n\n\t{unconfigured_project_names}\n\n")

@main.command()
@click.option('-m', '--monitor', default=False, is_flag=True, help="Tell swarmit to monitor the event logs right after the experiment starts")
def deploy(monitor):
    """Deploy a firmware to a set of DotBots."""
    dotbot_project = load_project_config("dotbot")

    # if needed, build dotbot and swarmit projects
    res = cmd.execute(dotbot_project.list_outputs_cmd, directory=dotbot_project.build_dir)
    if not res:
        do_build("dotbot", clean_build_first=False, is_interactive=False)
        res = cmd.execute(dotbot_project.list_outputs_cmd, directory=dotbot_project.build_dir)
        if not res:
            raise RuntimeError("Failed to build dotbot project")
    if not os.path.exists("build/swarmit"):
        do_build("swarmit", clean_build_first=False, is_interactive=False)

    # use swarmit to check the available devices
    res, stdout, stderr = cmd.execute_and_output("swarmit status")
    logging.info(f"Available devices:\n\n{stdout}\n\n")
    time.sleep(1)

    # deploy the firmware to the devices using swarmit
    res = cmd.execute("swarmit stop") # make sure experiment is not running
    if not res:
        logging.warning("Failed to stop the experiment")
        return
    time.sleep(2)
    res = cmd.execute_pretty(f"swarmit flash -y $PWD/build/dotbot/{dotbot_project.output_dir}/*.bin")
    time.sleep(1)
    if not res:
        raise RuntimeError("Failed to deploy firmware to devices")
    res = cmd.execute("swarmit start")
    if res:
        logging.info("Firmware deployed and experiment started")
    else:
        raise RuntimeError("Failed to start the experiment")
    if monitor:
        cmd.execute_pretty("swarmit monitor", is_interactive=True)

if __name__ == "__main__":
    main()
