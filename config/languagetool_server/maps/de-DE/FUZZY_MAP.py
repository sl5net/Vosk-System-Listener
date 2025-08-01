# FUZZY_MAP.py
import re

# This map uses a hybrid approach:
# 1. Regex entries are checked first. They are powerful and can be case-insensitive.
#    Structure: ('replacement', r'regex_pattern', threshold, flags)
#    - The threshold is ignored for regex.
#    - flags: Use re.IGNORECASE for case-insensitivity, or 0 for case-sensitivity.
# 2. If no regex matches, a simple fuzzy match is performed on the remaining rules.

FUZZY_MAP = [
    # === General Terms (Case-Insensitive) ===
    # Using word boundaries (\b) and grouping (|) to catch variations efficiently.
    ('.', r'^\s*(punkt|pup)\s*$', 82, re.IGNORECASE),


    ('CamelCase', r'^\s*kämme\s*Case\s*$', 82, re.IGNORECASE),
    ('pull requests', r'^\s*(pull\s*requests?|Pullover\s*Quest)\s*$', 82, re.IGNORECASE),

    ('pull requests', r'\b(null|pull) requests\b', 82, re.IGNORECASE),
    
    ('feature branch', r'\bFeature\s*prince\b', 82, re.IGNORECASE),
    ('git branch -d', r'\b(Branch|Prince)\s*löschen\b', 82, re.IGNORECASE),
    ('Branch Name', r'\bRanch\s*Namen\b', 82, re.IGNORECASE),
    ('Commit', r'\bkomm\s*mit\b', 82, re.IGNORECASE),
    ('Commit Message', r'\bkommen\s*mit\s*Message\b', 82, re.IGNORECASE),
    ('neues Release', r'\bneues\s*Verlies\b', 82, re.IGNORECASE),
    ('Code Abschnitt', r'\bKot\s*abschnittt\b', 82, re.IGNORECASE),
    ('StopButton', r'\bstob\s*Button\b', 82, re.IGNORECASE),
    ('lowerCase', r'\blobt\s*Case\b', 82, re.IGNORECASE),
    ('Lauffer', r'\b(Läufer|laufer)\b', 82, re.IGNORECASE), # Exact match, but ignore case

    # === Git Commands (Consolidated & Case-Insensitive) ===

    # --- git status ---
    # This one regex replaces 5 old entries.
    ('git status', r'^\s*(git|geht|gitter|kids)\s+(status|staates|dates)\s*$', 82, re.IGNORECASE),

    # --- git add . ---
    # geh tat geh tat
    # This one regex replaces over 15 old entries!
    ('git add .', r'^\s*(git|geht|geh|gitter|kate|fiat|mit)\s+(add|at|tat|dad|hat|duett|es)\s*(\.|\bpunkt\b)?\s*$', 82, re.IGNORECASE),

    # --- git commit ---
    ('git commit', r'^\s*(Geht|git|mit) (komm|Commit)\s*$', 80, re.IGNORECASE),


    ('git commit', r'^\s*(git|mit) komm\s*mit\s*$', 80, re.IGNORECASE),
    ('git commit', r'^\s*womit\s*$', 85, re.IGNORECASE),
    ('git commit -m "', r'^\s*(git|geht) komm?\s*mit\s*$"', 80, re.IGNORECASE),
    ('git commit -m "', r'^\s*(git|Gilt|geht) (Komet|komme)\s*$"', 80, re.IGNORECASE),
    # Gilt komme komme

    # --- git push ---
    ('git push', r'^\s*(git|geht|gitter)\s*(busch|push)\s*$', 85, re.IGNORECASE),

    # --- git pull ---
    ('git pull', r'^\s*(git|geht|gitter)\s*(pohl|pool)\s*$', 82, re.IGNORECASE),
    ('git pull', r'^\s*git\s*pull\s*$', 80, re.IGNORECASE),

    # --- git diff ---
    ('git diff', r'^\s*(git|geht|peach)\s*(diff|tief|juice)\s*$', 75, re.IGNORECASE),
]
