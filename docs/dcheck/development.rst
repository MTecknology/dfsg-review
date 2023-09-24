.. _dcheck-dev:

Dev Notes
=========

Data Workflow:

1. Source package uploaded (via dput) to ``pending_dir``
2. Unpack archive into ``workspace_dir/package``
3. Verify valid signature of uploaded package data
4. Run "automatic" checks, save as ``??``

Dependencies::

    # Core
    apt install python3-gnupg python3-redis python3-yaml
    # GUI
    apt install python3-tk
    # Web
    apt install python3-bottle

