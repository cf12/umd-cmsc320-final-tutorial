#!/bin/bash

jupyter nbconvert --execute --to html src/analysis.ipynb --output index.html --output-dir docs --HTMLExporter.theme=dark