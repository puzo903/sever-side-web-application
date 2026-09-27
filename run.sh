#!/bin/bash
export PYTHONPATH=./src
coverage run --branch -m pytest tests/
coverage report -m