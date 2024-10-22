# OpenSwarm implementation

It will work like this:
```bash
# there is a default file with baseline configs, including repo urls: _base.toml

# build firmware images for dotbots, according to build, flash, or run sections in config file
swarmake dotbot build

swarmake lakers build

swarmake freebot build

swarmake minimal-length-swarm-networks build
```