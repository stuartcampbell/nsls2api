# NSLS-II Facility API

This is the repository for the NSLS-II Facility API codebase. 

## Current Status

[![Integration Tests for Deployed API](https://github.com/NSLS2/nsls2api/actions/workflows/test-production-deployment.yml/badge.svg)](https://github.com/NSLS2/nsls2api/actions/workflows/test-production-deployment.yml)

## Developer Notes 

In order to develop locally you will need to have a local MongoDB running.  
This can be installed using your preferred method, a native install or running a container work perfectly fine.

Once you have MongoDB up and running you then need to 'seed' the facility and beamline information that 
does not get pulled from any other source.  The json files for the collections can be found at `/nsls2/software/dssi/nsls2core`

1. Copy the `beamlines.json` and `facilities.json` to your development machine

2. Import facility information into the local mongodb  
`mongoimport --db=nsls2core-development --collection=facilities --file=nsls2core.facilities.json`
3. Import beamline information into the local mongodb  
`mongoimport --db=nsls2core-development --collection=beamlines --file=nsls2core.beamlines.json`

You will then need to create a `.env` file that contains the configuration (an example can also be found in the same 
directory as the json files).

1. Copy `/nsls2/software/dssi/nsls2core/.env.development` to your local machine
2. Rename to `.env` and place in the `src/nsls2api` directory in your cloned repo (in the same folder as `main.py`)

### Updating Dependencies

The project uses `uv pip compile` to manage the `requirements.txt` and `requirements-dev.txt` files. 

In order to upgrade the packages you will need to simply run 

```
uv pip compile requirements-dev.in --upgrade -o requirements-dev.txt
uv pip compile requirements.in --upgrade -o requirements.txt
```

