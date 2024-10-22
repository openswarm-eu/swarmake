#!/usr/bin/env python

import os
import subprocess
import click
import shutil
import toml
# import logging
import sys
from tqdm import tqdm
from rich.console import Console
from rich.logging import RichHandler
from dataclasses import dataclass
from datetime import datetime
from itertools import cycle
import time

# import log
from openswarm.logger import setup_logging, LOGGER
logging = LOGGER.bind(context=__name__)

from openswarm.run_cmd import execute_command

# Load _base.toml configuration
BASE_CONFIG_FILE = "_base.toml"
config = toml.load(BASE_CONFIG_FILE)

console = Console()

@dataclass
class ProjectConfig:
    name: str
    url: str
    build_cmd: str = ""
    setup_cmd: str = ""
    run_cmd: str = ""
    list_outputs_cmd: str = ""

    @property
    def build_dir(self):
        return f"{config['_swarmake']['build-dir']}/{self.name}"

def load_project_config(project_name):
    project_key = project_name
    if project_key not in config["projects"]:
        raise ValueError(f"Project '{project_name}' not found in configuration.")
    
    project_data = config["projects"][project_key]
    repo_name = project_data.get("repo", project_name)  # If repo name is not explicitly defined, use project name
    build_cmd = project_data.get("build", "")
    setup_cmd = project_data.get("setup", "")
    run_cmd = project_data.get("run", "")
    list_outputs_cmd = project_data.get("list-outputs", "")
    
    return ProjectConfig(
        name=project_name,
        url=f"{config['_swarmake']['openswarm-url']}/{repo_name}",
        build_cmd=build_cmd,
        setup_cmd=setup_cmd,
        run_cmd=run_cmd,
        list_outputs_cmd=list_outputs_cmd,
    )

def clone_repository(url, destination):
    if not os.path.exists(destination):
        logging.info(f"Cloning repository", url=url, destination=destination)
        subprocess.run(["git", "clone", url, destination])
    else:
        logging.info(f"Repository already cloned.", url=url, destination=destination)

def clean_build_dir():
    """Clean the build directory for the specified project."""
    build_dir = f"{config['_swarmake']['build-dir']}"
    if os.path.exists(build_dir):
        logging.info(f"Cleaning build directory", build_dir=build_dir)
        shutil.rmtree(build_dir)
    else:
        logging.info(f"Build directory does not exist", build_dir=build_dir)

@click.group()
@click.pass_context
def main(ctx):
    log_level = "info"
    passed_level = os.environ.get("PYTHON_LOG").lower()
    if passed_level in ["debug", "info", "warning", "error"]:
        log_level = passed_level
    setup_logging("swarmake.log", log_level, ["console", "file"])

@main.command()
@click.option('-c', '--clean-build-first', default=False, is_flag=True, help="Clean the build directory before building")
@click.argument("project_name")
def build(project_name, clean_build_first):
    """Build the specified project"""

    if clean_build_first:
        clean_build_dir()

    project = load_project_config(project_name)

    # Clone the repository if necessary
    clone_repository(project.url, f"{config['_swarmake']['build-dir']}/{project.name}")

    # Execute the setup and build commands
    os.chdir(project.build_dir)
    try:
        if project.setup_cmd:
            logging.info(f"Running setup", project_name=project.name)
            execute_command(project.setup_cmd, project.name)
        execute_command(project.build_cmd, project.name)
        if project.list_outputs_cmd:
            execute_command(project.list_outputs_cmd, project.name)
    finally:
        os.chdir("..")

@main.command()
@click.option('-c', '--clean-build-first', default=False, is_flag=True, help="Clean the build directory before building")
@click.argument("project_name")
def run(project_name, clean_build_first):
    """Run the specified project"""
    project = load_project_config(project_name)

    # check if the project is cloned / built
    if not os.path.exists(f"{config['_swarmake']['build-dir']}/{project.name}"):
        raise ValueError(f"Project {project.name} has not been built. Please run 'swarmake build {project.name}' first.")
    
    # Execute the run command
    os.chdir(project.build_dir)
    try:
        execute_command(project.run_cmd, project.name)
    finally:
        os.chdir("..")

# add a dummy command
@main.command()
def dummy():
    logging.info("Dummy command executed")

if __name__ == "__main__":
    main()
