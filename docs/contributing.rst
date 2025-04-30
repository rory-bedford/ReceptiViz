Contributing Guide
==================

Thanks for contributing! This project uses ``uv`` for dependency management, ``pre-commit`` for code quality enforcement, and ``pytest`` for testing. Follow the steps below to get set up.

Setup
-----

1. **Clone the repository:**

   .. code-block:: bash

      git clone git@github.com:rory-bedford/Receptual.git
      cd Receptual

2. **Check development environment:**

   .. code-block:: bash

      uv sync
      uv run receptual

3. **Install pre-commit hooks:**

   .. code-block:: bash

      uv run pre-commit install

What Gets Linted/Formatted Automatically
----------------------------------------

On every commit, ``pre-commit`` will run:

- ``ruff check --fix`` — static analysis / linting
- ``ruff format`` — formats code
- ``pytest`` — runs unit tests

We then have a GitHub action that runs:

- ``ruff check``
- ``ruff format --check``
- ``pytest``

Any pull request will be blocked if any of these fail.

Run Checks Manually
-------------------

You can also run the formatting and checks manually anytime:

.. code-block:: bash

   uv run ruff check --fix         # Lint
   uv run ruff format              # Format check
   uv run pytest                   # Run tests

Guidelines
----------

- Code must be formatted (``ruff format``)
- Code must pass linting (``ruff check``)
- Code must be tested (``pytest``)
- All CI checks must pass before merging

Publishing
----------

Git tags pushed to ``main`` get built into a GitHub release, get pushed to PyPI, and have docs built and published by Read the Docs. This can only be done by administrators of the package.

Prior to doing so, make sure you:

- Update the version in ``pyproject.toml``
- Update the version in ``docs/conf.py``
- Add an entry to the changelog
- Commit these changes

Then you can run:

.. code-block:: bash

   git tag -a v*.*.* -m ':bookmark: v*.*.*'
   git push origin v*.*.*