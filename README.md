# swarmake  &emsp;  [![CI status]][actions] [![Latest Version]][pypi]

[CI status]: https://github.com/openswarm-eu/swarmake/workflows/Main%20Action/badge.svg
[actions]: https://github.com/openswarm-eu/swarmake/actions/workflows/main.yml
[Latest Version]: https://img.shields.io/pypi/v/swarmake?color=%2334D058&label=pypi%20package
[pypi]: https://pypi.org/project/swarmake

`swarmake` is a command-line tool for managing OpenSwarm components. It simplifies the process of fetching, building, and running various components of the OpenSwarm ecosystem, making it easier to work with robot swarms.

## Features

- 🔄 Automated build process for OpenSwarm components
- 📥 Automatically downloads repositories from the OpenSwarm GitHub organization
- 📡 Deployment tools with real-time monitoring of robot swarms
- 🛠️ Extensible recipe system for custom components

## Installation

Install `swarmake` using pip:

```bash
pip install swarmake
```

## Usage

For help with any command, use:
```bash
swarmake [command] --help
```

### Building Components

Build the DotBot firmware:
```bash
# Clone the dotbot repo and build it in Docker using the recipe in swarmake.toml
swarmake build dotbot
```

Build the Coaty Data Distribution Agent:
```bash
# Clone the repo and prepare the docker image
swarmake build dda
```

### Running Components

Build and run the `lakers` library:
```bash
# Build the lakers component
swarmake build lakers 2> /dev/null
# Run according to swarmake.toml configuration
swarmake run lakers
```

### Deploying Swarms

Deploy a swarm of DotBots with monitoring:
```bash
TARGET_APP=move swarmake deploy --monitor
```

This command will:
1. Clone & build the dotbot and swarmit projects
2. Flash the firmware to available dotbots
3. Start the experiment
4. Monitor and display logs from the dotbots

## Adding New Components

To add a new component to swarmake:
1. Open the `swarmake.toml` configuration file
2. Add your project with its repository URL in the `_core.repositories` section
3. Define recipes for:
   - `build` (optional): Build and setup instructions
   - `run` (optional): Commands to run the component
   - `repo` (optional): Override the repository name (uses project name by default)
   - `list-outputs` (optional): Command to list build outputs

Example configuration:
```toml
[project.mycomponent]
build = """
pip install mycomponent
"""
run = "./run-my-component.sh"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
