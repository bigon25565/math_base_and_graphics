#!/bin/bash
pyinstaller --onefile --add-data "images:images" --add-data "sounds:sounds" alien_invasion.py
