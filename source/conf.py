# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import alabaster
import better

project = 'Thoughts, et cetera'
copyright = '2023, Shreeyash Pandey'
author = 'Shreeyash Pandey'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinxcontrib.bibtex']
bibtex_bibfiles = ['refs.bib']
bibtex_default_style = 'plain'
bibtex_reference_style = 'super'

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_theme_path = [alabaster.get_path()]
html_static_path = ['_static']
html_css_files = ['css/custom.css']
