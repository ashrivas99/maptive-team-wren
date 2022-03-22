To start backend server, navigate to folder 'backend' on powershell and run below commands:

> $env:FLASK_APP = "maptive_backend_apis"
> $env:FLASK_ENV = "development"

To initialize DB, run on cmd:

> flask init-db (optional - only needed the first time)

To get the server up:

> flask run

Alternatively if using cmd, use below commands

> set FLASK_APP=maptive_backend_apis
> set FLASK_ENV=development
> flask init-db (optional - only needed the first time)
> flask run

Or the below for bash

$ export FLASK_APP=maptive_backend_apis
$ export FLASK_ENV=development
$ flask init-db (optional - only needed the first time)
$ flask run
