# D​u​n​g​eo​n​ ​H​u​n​t​e​r​ ​-​ ​(c​)​ ​D​ra​g​o​n​de​f​e​r​ ​2​02​5
# L​i​c​e​n​s​ed​ u​nd​e​r​ ​C​C​-​B​Y​-N​C​ ​4.​0

__creation__ = "12-05-2025"

import logging
import os
from datetime import datetime

# Dossier des logs
if not os.path.exists("logs"):
    os.makedirs("logs")
else: # Clean up old logs < 100KB
    for filename in os.listdir("logs"):
        file_path = os.path.join("logs", filename)
        if os.path.isfile(file_path) and os.path.getsize(file_path) < 100 * 1024:
            try:
                os.remove(file_path)
            except PermissionError:
                pass

# Nom unique basé sur la date/heure
log_filename = datetime.now().strftime("logs/session_%Y-%m-%d_%H-%M-%S.log")

# Configuration du logger
logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger()

