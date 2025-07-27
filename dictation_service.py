# File: STT/dictation_service.py
import os
import sys
from datetime import date

import random


# ==============================================================================
# --- PREREQUISITE 1: VIRTUAL ENVIRONMENT CHECK ---
# The script MUST run inside its virtual environment to find dependencies.
# The 'VIRTUAL_ENV' variable is a standard indicator for an active venv.

if 'VIRTUAL_ENV' not in os.environ:
    print(
        "\nFATAL: Python virtual environment not activated!",
        file=sys.stderr
    )
    print(
        "       Please activate it first. On Linux/macOS, run:",
        file=sys.stderr
    )
    print("       source .venv/bin/activate", file=sys.stderr)
    print(
        "       Then, you can run the script: python dictation_service.py",
        file=sys.stderr
    )

    print("       Or (recommended) run:", file=sys.stderr)
    print(
        "       scripts/restart_venv_and_run-server.sh or run scripts/activate-venv_and_run-server.sh",
        file=sys.stderr
    )
    sys.exit(1)



# ==============================================================================






import sys, time, os, atexit, requests, logging, platform
from pathlib import Path

# --- Local Imports (grouped for clarity) ---
from config.settings import (LANGUAGETOOL_RELATIVE_PATH,
                            USE_EXTERNAL_LANGUAGETOOL, EXTERNAL_LANGUAGETOOL_URL, LANGUAGETOOL_PORT,
                            CRITICAL_THRESHOLD_MB, PRELOAD_MODELS,
                            DEV_MODE
                            )


from scripts.py.func.main import main
from scripts.py.func.notify import notify
from scripts.py.func.cleanup import cleanup
from scripts.py.func.start_languagetool_server import start_languagetool_server
from scripts.py.func.stop_languagetool_server import stop_languagetool_server
from scripts.py.func.check_memory_critical import check_memory_critical
# We need vosk here for the model loading
import vosk

from scripts.py.func.create_required_folders import setup_project_structure



# --- Constants and Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
# ==============================================================================
# --- PRE-RUN SETUP VALIDATION ---
# We add the 'scripts' directory to the path to import our custom validator.
sys.path.append(os.path.join(SCRIPT_DIR, 'scripts'))
from scripts.py.func.checks.setup_validator import validate_setup, check_for_unused_functions
from scripts.py.func.checks.validate_punctuation_map_keys import validate_punctuation_map_keys

from  scripts.py.func.checks.self_tester import run_core_logic_self_test

from  scripts.py.func.checks.check_example_file_is_synced import check_example_file_is_synced
check_example_file_is_synced(SCRIPT_DIR)



# Execute the check. The script will exit here if the setup is incomplete.
validate_setup(SCRIPT_DIR)

# File: STT/dictation_service.py
# ...
# --- Wrapper Script Check ---
if DEV_MODE :
    check_for_unused_functions(SCRIPT_DIR)
    validate_punctuation_map_keys(SCRIPT_DIR)

    #sys.exit(1)

# ==============================================================================
# ==============================================================================
# ==============================================================================



PROJECT_ROOT = SCRIPT_DIR # In this structure, SCRIPT_DIR is PROJECT_ROOT

setup_project_structure(PROJECT_ROOT)

if platform.system() == "Windows":
    TMP_DIR = Path("C:/tmp")
else:
    TMP_DIR = Path("/tmp")

TRIGGER_FILE = TMP_DIR / "vosk_trigger"
HEARTBEAT_FILE = TMP_DIR / "dictation_service.heartbeat"
PIDFILE = TMP_DIR / "dictation_service.pid"
LOG_DIR = PROJECT_ROOT / "log"
LOG_FILE = LOG_DIR / "dictation_service.log"

if __name__ == "__main__":
    # --- NEW: Log rotation logic at the very start ---
    log_path = Path(LOG_DIR) / LOG_FILE
    if log_path.exists():
        log_mod_date = date.fromtimestamp(log_path.stat().st_mtime)
        if log_mod_date < date.today():
            # Using print because the logger might not be configured yet
            print(f"Log file from {log_mod_date} is outdated. Deleting old log.")
            log_path.unlink()




PROJECT_ROOT = Path(__file__).resolve().parent
LANGUAGETOOL_JAR_PATH = PROJECT_ROOT / LANGUAGETOOL_RELATIVE_PATH


suspicious_events = []
if platform.system() == "Windows":
    TMP_DIR = Path("C:/tmp")
    NOTIFY_SEND_PATH = None
else:
    TMP_DIR = Path("/tmp")
OUTPUT_FILE = TMP_DIR / "tts_output.txt"
TRIGGER_FILE = TMP_DIR / "vosk_trigger"

HEARTBEAT_FILE = TMP_DIR / "dictation_service.heartbeat"
PIDFILE = TMP_DIR / "dictation_service.pid"
LOG_FILE = Path("log/dictation_service.log")

SCRIPT_DIR = Path(__file__).resolve().parent
LANGUAGETOOL_JAR_PATH = f"{SCRIPT_DIR}/LanguageTool-6.6/languagetool-server.jar"

languagetool_process = None



# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)-8s - %(message)s',
    handlers=[
        logging.FileHandler(f'{SCRIPT_DIR}/log/dictation_service.log', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()


# ==============================================================================
# --- Wrapper Script Check ---
# if not DEV_MODE and os.environ.get("DICTATION_SERVICE_STARTED_CORRECTLY") != "true":
#     logger.fatal("FATAL: This script must be started using the 'activate-venv_and_run-server.sh' wrapper.")
#     sys.exit(1)
# ==============================================================================



from scripts.py.func.notify import notify
from scripts.py.func.cleanup import cleanup
from scripts.py.func.start_languagetool_server import start_languagetool_server
from scripts.py.func.stop_languagetool_server import stop_languagetool_server
from scripts.py.func.transcribe_audio_with_feedback import transcribe_audio_with_feedback
from scripts.py.func.check_memory_critical import check_memory_critical
from scripts.py.func.stop_languagetool_server import stop_languagetool_server
from scripts.py.func.guess_lt_language_from_model import guess_lt_language_from_model

files_to_clean = [HEARTBEAT_FILE, PIDFILE, TRIGGER_FILE]
atexit.register(lambda: cleanup(logger, files_to_clean))
atexit.register(lambda: stop_languagetool_server(logger, languagetool_process))

with open(PIDFILE, 'w') as f:
    f.write(str(os.getpid()))

# --- Argument Parsing und Model-Setup ---
MODEL_NAME_DEFAULT = "vosk-model-de-0.21" # fallback

SCRIPT_DIR = Path(__file__).resolve().parent

""""
parser = argparse.ArgumentParser(description="A real-time dictation service using Vosk.")
parser.add_argument('--vosk_model', help=f"Name of the Vosk model folder. Defaults to '{MODEL_NAME_DEFAULT}'.")
parser.add_argument('--test-text', help="Bypass microphone and use this text for testing.")
args = parser.parse_args()
VOSK_MODEL_FILE = SCRIPT_DIR / "config/model_name.txt"
vosk_model_from_file = Path(VOSK_MODEL_FILE).read_text().strip() if Path(VOSK_MODEL_FILE).exists() else ""
MODEL_NAME = args.vosk_model or vosk_model_from_file or MODEL_NAME_DEFAULT

"""





TRIGGER_FILE.unlink(missing_ok=True)

# MODEL_PATH = SCRIPT_DIR / "models" / MODEL_NAME

import scripts.py.func.guess_lt_language_from_model

# LT_LANGUAGE = guess_lt_language_from_model(MODEL_NAME)




active_lt_url = None

if USE_EXTERNAL_LANGUAGETOOL:
    logger.warning(f"USING EXTERNAL LT SERVER: {EXTERNAL_LANGUAGETOOL_URL}. AT YOUR OWN RISK.")
    active_lt_url = EXTERNAL_LANGUAGETOOL_URL
    # PING-TEST:
    try:
        requests.get(f"{active_lt_url}/v2/languages", timeout=3)
        logger.info("External LanguageTool server is responsive.")
    except requests.exceptions.RequestException:
        logger.fatal("External LanguageTool server did not respond. Is it running?")
        sys.exit(1)
else:
    PROJECT_ROOT = Path(__file__).resolve().parent
    jar_path_absolute = PROJECT_ROOT / LANGUAGETOOL_RELATIVE_PATH
    internal_lt_url = f"http://localhost:{LANGUAGETOOL_PORT}"

    logger.info(f"start_languagetool_server(logger, {jar_path_absolute}, {internal_lt_url})")
    languagetool_process = start_languagetool_server(logger, jar_path_absolute, internal_lt_url)
    if not languagetool_process: sys.exit(1)
    atexit.register(lambda: stop_languagetool_server(logger, languagetool_process))

    active_lt_url = f"http://localhost:{LANGUAGETOOL_PORT}/v2/check"


if not start_languagetool_server:
    notify("Vosk Startup Error", "LanguageTool Server failed to start.", "critical")
    sys.exit(1)


    from scripts.py.func.checks.integrity_checker import check_code_integrity # <--- NEU


if DEV_MODE :
    from scripts.py.func.checks.setup_validator import check_for_unused_functions
    from scripts.py.func.checks.validate_punctuation_map_keys import validate_punctuation_map_keys
    from scripts.py.func.checks.integrity_checker import check_code_integrity

    from scripts.py.func.checks.self_tester import run_core_logic_self_test


    check_for_unused_functions(SCRIPT_DIR)
    validate_punctuation_map_keys(SCRIPT_DIR)
    check_code_integrity(SCRIPT_DIR, logger)

    ##################### run_core_logic_self_test #############################
    VOSK_MODEL_FILE = SCRIPT_DIR / "config/model_name.txt"
    vosk_model_from_file = Path(VOSK_MODEL_FILE).read_text().strip() if Path(VOSK_MODEL_FILE).exists() else ""
    #MODEL_NAME = MODEL_NAME_DEFAULT

    lang_code = guess_lt_language_from_model(vosk_model_from_file)



# CODE_LANGUAGE_DIRECTIVE: ENGLISH_ONLY
# file: dictation_service.py




# TODO: implement:  --skip-self-test

if random.randint(1, 5) == 1:
    logger.info("Running randomized self-test...")
    run_core_logic_self_test(logger, TMP_DIR, active_lt_url,lang_code)

else:
    logger.info("Skipping randomized self-test.")
    #sys.exit(1)

"""
Ja, deine Vermutung ist absolut richtig.

Der run_core_logic_self_test ist der Prozess, der die vollen ~48 Sekunden in Anspruch nimmt. Der "integrity check" ist nur der allererste Schritt davon.

Die meiste Zeit innerhalb dieses Tests wird für zwei Dinge verbraucht:

Start des LanguageTool-Servers (ca. 30-40 Sek.): Das Skript startet einen Java-Prozess (java -jar ...) und wartet dann in einer Schleife bis zu 20 Sekunden darauf, dass der Server antwortet. Das ist der mit Abstand langsamste Teil.

Laden des Vosk-Modells (ca. 5-10 Sek.): Das Sprachmodell muss in den Arbeitsspeicher geladen werden, was ebenfalls einige Sekunden dauert.

Die eigentlichen 8 Tests (Audio transkribieren etc.) sind danach blitzschnell. Du wartest also hauptsächlich auf das Hochfahren der externen Dienste.
"""





# --- main-logic is in Thread ---

recording_time = 0
from config import settings # Import the whole settings module
if __name__ == "__main__":
    # 1. Load all settings from the module into a dictionary
    config = {key: getattr(settings, key) for key in dir(settings) if key.isupper()}

    # 2. Add/overwrite dynamic, script-specific values
    config.update({
        "SCRIPT_DIR": SCRIPT_DIR,
        "TMP_DIR": TMP_DIR,
        "HEARTBEAT_FILE": HEARTBEAT_FILE,
        "PIDFILE": PIDFILE,
        "TRIGGER_FILE": TRIGGER_FILE,
        "PROJECT_ROOT": PROJECT_ROOT
    })



    # --- Plugin State Communication ---
    # Create a flag file so client scripts know if a plugin is active.
    try:
        auto_enter_flag_path = "/tmp/sl5_auto_enter.flag"
        auto_enter_enabled = settings.PLUGINS_ENABLED.get("auto_enter_after_dictation", False)
        with open(auto_enter_flag_path, "w") as f:
            f.write(str(auto_enter_enabled).lower()) # Writes 'true' or 'false'
        logger.info(f"Set auto-enter flag to: {auto_enter_enabled}")
    except Exception as e:
        logger.error(f"Could not write auto-enter flag file: {e}")



    # Pass the complete, unified config to main()
    loaded_models = {}
    main(logger, loaded_models, config, suspicious_events, recording_time, active_lt_url)

