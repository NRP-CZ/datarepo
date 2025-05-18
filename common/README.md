# `common` folder

This folder contains your shared packages - packages that
are used by multiple models/uis in the monorepo.

Feel free to add any python/resources here. If you need to
reference external packages, add them to `project.toml`.

## Usage

This folder is automatically installed to the running repository
when `nrp build` or `nrp develop` is called. You can then import
the modules in your models/uis as follows:

```python
from common import my_module
```
