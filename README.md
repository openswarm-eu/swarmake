# OpenSwarm implementation

Fetch, build, and run the OpenSwarm.

## Examples
The Atlas simulation project:
```bash
swarmake build atlas # clone the atlas repo and build it using the recipe defined in swarmake.toml
swarmake run atlas # run it using the recibe in swarmake.toml
```

The DotBot firmware:
```bash
# clone the dotbot repo and build it in Docker, using the recipe defined in swarmake.toml
swarmake build dotbot
```

The Lakers library
```bash
# clone the lakers repo and build it using the recipe defined in swarmake.toml
# when stderr is redirected, we suppress stdout too and just show a "loading" line
swarmake build lakers 2> /dev/null
# run according to swarmake.toml
swarmake run lakers
```
