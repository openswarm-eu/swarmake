# OpenSwarm implementation

Fetch, build, and run the OpenSwarm.

## Examples
The Atlas simulation project:
```bash
swarmake build atlas # clone the atlas repo and build it using the recipe defined in _base.toml
swarmake run atlas # run it using the recibe in _base.toml
```

The DotBot firmware:
```bash
# clone the dotbot repo and build it in Docker, using the recipe defined in _base.toml
swarmake build dotbot
```

The Lakers library
```bash
# clone the lakers repo and build it using the recipe defined in _base.toml
# when stderr is redirected, we suppress stdout too and just show a "loading" line
swarmake build lakers 2> /dev/null
# run according to _base.toml
swarmake run lakers
```
