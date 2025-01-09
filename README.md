# NSLS-II Facility API

This is the repository for the NSLS-II Facility API codebase. 

## Current Status

[![Integration Tests for Deployed API](https://github.com/NSLS2/nsls2api/actions/workflows/test-production-deployment.yml/badge.svg)](https://github.com/NSLS2/nsls2api/actions/workflows/test-production-deployment.yml)

## Developer Notes 



### Updating Dependencies

The project uses `uv pip compile` to manage the `requirements.txt` and `requirements-dev.txt` files. 

In order to upgrade the packages you will need to simply run 

```
uv pip compile requirements-dev.in --upgrade -o requirements-dev.txt
uv pip compile requirements.in --upgrade -o requirements.txt
```

