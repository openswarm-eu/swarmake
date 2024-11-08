#!/usr/bin/env python

import os
import subprocess
import click
import shutil

from swarmake.logger import setup_logging, LOGGER
logging = LOGGER.bind(context=__name__)

from swarmake.cmd import execute_command
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
@click.pass_context
def main(ctx):
    log_level = "info"
    passed_level = os.environ.get("PYTHON_LOG", "").lower()
    if passed_level in ["debug", "info", "warning", "error"]:
        log_level = passed_level
    setup_logging("swarmake.log", log_level, ["console", "file"])

@main.command()
@click.option('-c', '--clean-build-first', default=False, is_flag=True, help="Clean the build directory before building")
@click.argument("project_name")
def build(project_name, clean_build_first):
    """Build the specified project"""

    print("\n\n================================================================================")
    print("                                 BUILDING")
    print("================================================================================\n\n")

    if clean_build_first:
        clean_build_dir(project_name)

    project = load_project_config(project_name)

    # Clone the repository if necessary
    clone_repository(project.url, project.build_dir)

    # Execute the setup and build commands
    os.chdir(project.build_dir)
    try:
        if project.setup_cmd:
            logging.info(f"Running setup", project_name=project.name)
            execute_command(project.setup_cmd, project.name)
        execute_command(project.build_cmd, project.name)
        if project.list_outputs_cmd:
            logging.info(f"Listing outputs", project_name=project.name)
            execute_command(project.list_outputs_cmd, project.name, force_show_output=True)
    finally:
        os.chdir("..")

@main.command()
@click.option('-c', '--clean-build-first', default=False, is_flag=True, help="Clean the build directory before building")
@click.argument("project_name")
def run(project_name, clean_build_first):
    """Run the specified project"""
    project = load_project_config(project_name)

    # check if the project is cloned / built
    if not os.path.exists(f"{config.core.build_dir}/{project.name}"):
        raise ValueError(f"Project {project.name} has not been built. Please run 'swarmake build {project.name}' first.")
    
    # Execute the run command
    os.chdir(project.build_dir)
    try:
        execute_command(project.run_cmd, project.name)
    finally:
        os.chdir("..")

# command to list available projects
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

# add a dummy command
@main.command()
def dummy():
    logging.info("Dummy command executed")

if __name__ == "__main__":
    main()
