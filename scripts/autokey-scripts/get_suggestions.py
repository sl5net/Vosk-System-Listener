import subprocess
import time
from pathlib import Path
import os

readmeBuckup = """
xdotool key --clearmodifiers ctrl+Left ctrl+shift+Right && sleep 0.1 && xdotool key --clearmodifiers ctrl+c && sleep 0.1 && /home/seeh/projects/py/STT/vosk-tts/bin/python ~/projects/py/STT/get_suggestions.py
command = 'xdotool click 2 && sleep 0.1 && xdotool key --clearmodifiers "ctrl+c" && sleep 0.1 && /home/seeh/projects/py/STT/vosk-tts/bin/python ~/projects/py/STT/get_suggestions.py'
system . exec_command (command)
Mond
"""

keyboard.send_keys('<ctrl>+<left>')
keyboard.send_keys('<ctrl>+<shift>+<right>')
keyboard.send_keys('<ctrl>+c')
time.sleep(0.2)

command = '/home/seeh/projects/py/STT/vosk-tts/bin/python ~/projects/py/STT/get_suggestions.py'
system.exec_command (command)

#  ( düst | tust | des | Nest | lest | Pest | duzt | West | tost | Rest | döst | käst | fest | teste | säst | Fest | desto | Test )
# Mond 






