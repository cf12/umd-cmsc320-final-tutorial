#!/bin/bash

jupyter nbconvert --execute --to html src/prose.ipynb --output index.html --output-dir docs --HTMLExporter.theme=dark