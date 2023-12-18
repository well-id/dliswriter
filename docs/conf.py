# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DLIS Writer'
copyright = '2023, Well ID'
author = 'Dominika Dlugosz, Kamil Grunwald, Omer Faruk Sari'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list[str] = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Add an "Edit on GitHub" link to the top of all pages
html_context = {
    "display_github": True,
    "github_user": "well-id",
    "github_repo": "dlis-writer",
    "github_version": "main",
    "conf_py_path": "/docs/",
}