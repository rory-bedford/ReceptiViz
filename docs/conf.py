# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Receptual'
copyright = '2025, Rory Bedford'
author = 'Rory Bedford'
release = 'v0.1.4'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['autoapi.extension']
autoapi_type = 'python'
autoapi_dirs = ['../src/receptual']
autoapi_generate_api_docs = False

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_theme_options = {
	'description': 'A simple tool for computing and visualising neuron receptive fields',
	'fixed_sidebar': True,
	'logo': 'logo_white.png',
	'logo_name': True,
	'github_button': True,
	'github_repo': 'Receptual',
	'github_user': 'rory-bedford',
	'show_powered_by': False,
}
