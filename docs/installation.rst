Installation
============

Receptual is a pure Python package, and is available on `PyPI <https://pypi.org/project/receptual/>`_. We strongly recommend using a virtual environment for your installation. We suggest `uv <https://docs.astral.sh/uv/>`_ as a package/environment manager, but Receptual can also be installed with `conda <https://docs.conda.io/en/latest/>`_ or venv + pip.

Note that Receptual requires Python 3.13 or later.

uv 
---

.. code-block:: bash

	# Create a new environment with Python 3.13
	uv venv $HOME/venvs/receptual --python 3.13 # or wherever you keep your environments

	# Activate the environment
	source $HOME/venvs/receptual/bin/activate

	# Install Receptual
	uv pip install receptual

conda
-----

.. code-block:: bash

	# Create a new environment with Python 3.13
	conda create -n receptual python=3.13

	# Activate the environment
	conda activate receptual

	# Install Receptual
	pip install receptual

You can then launch Receptual in your activated environment with:

.. code-block:: bash

	receptual