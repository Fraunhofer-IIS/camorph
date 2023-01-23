# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('.\\lib'))
#sys.path.insert(0, os.path.abspath('.\\lib\\utils'))
#sys.path.insert(0, os.path.abspath('.\\lib\\model'))
sys.path.insert(0, os.path.abspath('.\\ext'))
#sys.path.insert(0, os.path.abspath('.\\ext\\COLMAP'))

# -- Project information -----------------------------------------------------

project = 'camorph'
copyright = '2022, Benjamin Brand'
author = 'Benjamin Brand'

# The full version, including alpha/beta/rc tags
release = '02.04.2022'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx.ext.autodoc', 'sphinx_rtd_theme', 'sphinxcontrib.confluencebuilder', 'sphinx_markdown_builder']
autodoc_typehints = "none"

myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "inv_link",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Confluence options
confluence_publish = True
confluence_space_key = 'BTCIAS'
confluence_ask_password = True
confluence_server_url = 'https://intern.iis.fhg.de/'
confluence_server_user = 'brandbn'
confluence_parent_page = 'brandbn::Bachelor_thesis_camorph::Documentation'