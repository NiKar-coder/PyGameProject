@echo off
PyGameProject\Scripts\pyinstaller.exe --windowed --noconfirm --onefile --clean --icon "data\images\skydiver.png" --name "Skydiver" main.py
PyGameProject\Scripts\pyinstaller.exe --windowed --noconfirm --onefile --distpath "." --icon "data\images\skydiver.png" --name "Skydiver" main.py
