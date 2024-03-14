# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import os
import sys
from importlib.metadata import version

# Define path to the code to be documented **relative to where conf.py (this file) is kept**
sys.path.insert(0, os.path.abspath("../src/"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "hipscat-import"
copyright = "2023, LINCC Frameworks"
author = "LINCC Frameworks"
release = version("hipscat-import")
# for example take major/minor
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = []
exclude_patterns = ["_build", "**.ipynb_checkpoints"]

# This assumes that sphinx-build is called from the root directory
master_doc = "index"

html_theme = "sphinx_book_theme"

html_static_path = ["_static"]
html_css_files = ["custom.css"]

extensions = [
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "autoapi.extension",
    "nbsphinx",
]

# -- autoapi configuration ----------------------------------------
# Remove 'view source code' from top of page (for html, not python)
html_show_sourcelink = False
# Remove namespaces from class/method signatures
add_module_names = False

autoapi_type = "python"
autoapi_dirs = ["../src"]
autoapi_ignore = ["*/__main__.py", "*/_version.py"]
autoapi_add_toc_tree_entry = False
autoapi_member_order = "bysource"

napoleon_google_docstring = True

# -- sphinx-copybutton configuration ----------------------------------------
## sets up the expected prompt text from console blocks, and excludes it from
## the text that goes into the clipboard.
copybutton_exclude = ".linenos, .gp"
copybutton_prompt_text = ">> "

## lets us suppress the copy button on select code blocks.
copybutton_selector = "div:not(.no-copybutton) > div.highlight > pre"
