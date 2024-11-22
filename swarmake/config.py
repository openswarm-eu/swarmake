from dataclasses import dataclass, field
from typing import List, Dict
import importlib.resources as pkg_resources
import toml
import os

SWARMAKE_CONFIG_FILE = "swarmake.toml"
if not os.path.exists(SWARMAKE_CONFIG_FILE):
    # if the file is not found in the current directory, use the default one from the installed package
    SWARMAKE_CONFIG_FILE = str(pkg_resources.files("swarmake").joinpath("swarmake.toml"))

# global configuration object
config = None

@dataclass
class ProjectConfig:
    """Configuration related to a single project"""
    name: str
    repo_name: str
    build_cmd: str = ""
    setup_cmd: str = ""
    run_cmd: str = ""
    list_outputs_cmd: str = ""
    output_dir: str = ""

    @property
    def build_dir(self):
        return f"{config.core.build_dir}/{self.name}"

    @property
    def url(self):
        return f"{config.core.openswarm_url}/{self.repo_name}"

@dataclass
class CoreConfig:
    """Core configuration (_core section of the TOML)"""
    openswarm_url: str
    repositories: List[str]
    build_dir: str

@dataclass
class SwarmakeConfig:
    """SwarmakeConfig class to manage the entire configuration (core and projects)"""
    core: CoreConfig
    projects: Dict[str, ProjectConfig] = field(default_factory=dict)

    @classmethod
    def from_toml(cls, toml_file: str):
        raw_config = toml.load(toml_file)
        # Load core configuration
        core_config = CoreConfig(
            openswarm_url=raw_config["_core"]["openswarm-url"],
            repositories=raw_config["_core"]["repositories"],
            build_dir=raw_config["_core"]["build-dir"],
        )
        # Load project configurations
        projects = {}
        for project_name, project_data in raw_config["projects"].items():
            repo_name = project_data.get("repo", project_name)
            projects[project_name] = ProjectConfig(
                name=project_name,
                repo_name=repo_name,
                build_cmd=project_data.get("build", ""),
                setup_cmd=project_data.get("setup", ""),
                run_cmd=project_data.get("run", ""),
                list_outputs_cmd=project_data.get("list-outputs", ""),
                output_dir=project_data.get("output-dir", ""),
            )
        return cls(core=core_config, projects=projects)

config = SwarmakeConfig.from_toml(SWARMAKE_CONFIG_FILE)
