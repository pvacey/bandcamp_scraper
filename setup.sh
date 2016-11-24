#!/bin/bash
rm -rf venv
mkdir venv
virtualenv venv
venv/bin/pip install pymongo requests[security]
