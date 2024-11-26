# swarmake  &emsp;  [![CI status]][actions] [![Latest Version]][pypi]

[CI status]: https://github.com/openswarm-eu/swarmake/workflows/Main%20Action/badge.svg
[actions]: https://github.com/openswarm-eu/swarmake/actions/workflows/main.yml
[Latest Version]: https://img.shields.io/pypi/v/swarmake?color=%2334D058&label=pypi%20package
[pypi]: https://pypi.org/project/swarmake

Fetch, build, and run the OpenSwarm.

For help, use `swarmake [command] --help`.

# Examples

## Build
Build the DotBot firmware:
```bash
# clone the dotbot repo and build it in Docker, using the recipe defined in swarmake.toml
swarmake build dotbot
```

Build the Coaty Data Distribution Agent:
```bash
# clone the repo and prepare the docker image
swarmake build dotbot
```

## Run
Build and run the `lakers` library:
```bash
# clone the lakers repo and build it using the recipe defined in swarmake.toml
# when stderr is redirected, we suppress stdout too and just show a "loading" line
swarmake build lakers 2> /dev/null
# run according to swarmake.toml
swarmake run lakers
```

## Deploy
Deploy a Swarm of DotBots:
```bash
TARGET_APP=move swarmake deploy --monitor
```

The command above will:
1. clone & build the dotbot and swarmit projects
2. flash the firmware to one or more available dotbots
3. start the experiment (i.e. run the firmware)
4. keep monitoring logs sent from dotbots
