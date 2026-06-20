@echo off
python -m PyInstaller --onefile --add-data "images;images" --add-data "sounds;sounds" alien_invasion.py
pause