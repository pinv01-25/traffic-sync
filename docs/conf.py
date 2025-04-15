import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "traffic-sync"
copyright = "2025, Kevin Galeano"
author = "Kevin Galeano"
release = "1.0.0"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

add_module_names = False
