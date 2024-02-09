# NSLS-II Facility API

This is the repository for the NSLS-II Facility API codebase. 


### Updating Dependencies

The project uses `pip-compile` to manage the `requirements.txt` and `requirements-dev.txt`. 
In order to upgrade the packages you will need to install `pip-tools`.  Then to upgrade simply run 

```
pip-compile requirements-dev.in --upgrade
pip-compile requirements.in --upgrade
```

