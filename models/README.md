# `models` folder

This folder contains your models. Models are the core of your
repository - they define the structure of your metadata and how
it is stored in the database.

## Usage

## Adding new model

```bash
nrp model create <model-name>
```

Will create a template for a new model. When finished, you can
start modifying the metadata schema of the model to suit your needs.
When you are done, compile the model.

## Compiling models

```bash
nrp model compile <model-name>
```

This command will compile your model into invenio sources. You should
not modify those sources directly, as they will be overwritten when
you recompile the model.
