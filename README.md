# CESNET Data Repository

## Repository layout

The repository contains the following files and directories:

- `oarepo.yaml` - the main configuration file for the repository
- `pyproject.toml` - python dependencies and plugins
- `ui` - directory containing the UI sources, such as title page, search page, record detail page, etc.
  - `ui/branding` - branding information, including colors, logo, favicon etc.
- `tests` - directory containing tests for the repository
- `shared` - directory with shared code, local implementation etc.
- `nrp` - the nrp command line tool

The following files/directories are generated automatically
and should not be modified:

- `.venv` - virtual environment for the repository
- `.venv-*` - additional virtual environments for tools

## Basic commands

### Checking requirements

To check that the requirements are met, type:

```bash
nrp check
```

This will check that all the requirements are met
and the repository can be run. If there are any errors,
they will be reported and the command will exit with
a non-zero exit code.

To fix the problems, run the command with '--fix' option:

```bash
nrp check --fix
```

### Running the repository in development mode

To run the repository in development mode, type:

```bash
nrp develop --extra-library <path-to-library>
```

This will check the prerequisites, start the docker containers,
install the python dependencies, compile UI and start the development
server. The UI will be available at <https://127.0.0.1:5000>, the API
at <https://127.0.0.1:5000/api>

If `extra-library` parameter is given, this library will be installed
in an editable mode to the repository's virtual environment. You can
repeat this parameter multiple times to install multiple libraries.

Removal of extra libraries can be done by:
- calling `nrp build` or `nrp upgrade` commands
- removing the `.venv` directory and calling `nrp develop` again

After the first run of `nrp develop`, you can speed up the subsequent
runs by adding `--skip-checks` commandline option.

### Building the repository for production

```bash
nrp build
```

This will build the repository for production. It will check that
the python dependencies are up to date (to skip the check, run
`nrp build --skip-checks`). It will also clear the virtual environment
and reinstall all the dependencies before building the repository.

### Running the repository in production mode

To run the repository in production mode, type:

```bash
nrp run
```

This will just run the repository, depending on it having been built
beforehand. If the repository has not been built, it will fail.

In production mode, python/js sources are not watched for changes,
and the UI is build beforehand with minification and optimizations.

### Creating production images

To create a production image, type:

```bash
nrp image <image-name> <image-tag> <image-tag>
```

This will create a production image with the given name and tags.
The production image will be based on the `oarepo:oarepo-base-production:<invenio-version>`.
The image will be tagged with the given tags and also with the
`<image-name>:latest` tag.

This steps expects that the repository has been built beforehand.
If not it will fail.

Note: the image will not be pushed to the registry. To push the image
to the registry, use the `docker push` command.

### Testing the repository

To run test scenarios (integration API tests and UI tests), type:

```bash
nrp test
```

This command will create new containers, run the API tests and UI tests
within the docker then destroy the database. If any of the tests fail,
it will report the failure and exit with a non-zero exit code.

The command expects the repository to be built beforehand. If not, it
will fail.

### Upgrading dependencies of the repository

Run the following command to upgrade the dependencies of the repository:

```bash
nrp upgrade
```

This will upgrade the dependencies of the repository to the latest
versions (python and node dependencies). After this it will run the
build via `nrp build --production` and `nrp test` to make sure that
the dependencies will build.

## Handling models

### Creating new models

To create a new model, type:

```bash
nrp model create <model-name>
```

The command will ask a couple of questions and will create
`<model-name>.yaml` file in the `models` directory.
Please edit the file to add the fields and other information
about the model.

### Compiling and installing the model

To compile the model, type:

```bash
nrp model compile <model-name>
```

This will compile the model and generate python code for it.
The generated sources and entrypoints are placed in the
`<model-name>` directory and to `pyproject.toml` file.

Alembic migrations will be generated (this requires that the containers
are running - run `nrp develop` or `nrp check` before running this command).

After the model is compiled, run `nrp develop` and check that the
model is working correctly under the `/api` endpoint.

## Handling UI

### Creating UI pages for models

To create UI pages for a model, type:

```bash
nrp ui model create --model <model-name> <ui-name>
```

The `ui-name` is optional, if not specified, it will be the same
as the `model-name`. The command will ask a couple of questions
and will create jinjax templates and react pages for displaying
a listing of the model, a detail page and a form for creating
and editing the model.

### Creating UI pages for custom endpoints

To create UI pages for a custom endpoint, type:

```bash
nrp ui page create <page-name> <page-endpoint>
```

The `page-endpoint` is the endpoint of the page, for example
`/about` or `/search`. The `page-name` is the name of the page,
for example `about` or `search`.

If `page-endpoint` is not specified, it will be the same as
`page-name`.

The command will create a jinjax template for the page and register
the page to the flask application.

If you run the command with `--react` option, it will also create
react endpoint for the page and reference it from the jinjax template.
