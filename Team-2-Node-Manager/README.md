# Node-Manager

## Assumption

- Current Module folders just have **dummy data** which has specified file _(Might change as the project matures)_
- It is assumed that all the modules have a main working file with `module-name.py`.
- `Dockerfile` is created on the runtime and API endpoints are exposed to manage them.
- `create-node` will show an error that node with this name is already running. But it will run successfully once

## API Endpoints

These are the API endpoints that are managed by Node-Manager Module

- **/init**
- **/create_node/\<service-name\>**
- **/start_node/\<service-name\>**
- **/stop_node/\<service-name\>**
- **/restart_node/\<service-name\>**
- **/configure_node/\<service-name\>**

## Steps to execute

These steps are to be executed when your `pwd` is Node-Manager

```sh
$ pip install -r requirements.txt

$ uvicorn main:app --reload
```

Move to `localhost:8000/docs`, this will open an environement to test all the API's created.
