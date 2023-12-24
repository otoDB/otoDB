@echo off

flake8 . --ignore=E221,E222,E241,E501,F401
ruff .