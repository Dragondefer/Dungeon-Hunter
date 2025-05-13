__version__ = "4.0"
__creation__ = "12-05-2025"

import logging
import os
from datetime import datetime

# Dossier des logs
if not os.path.exists("logs"):
    os.makedirs("logs")

# Nom unique basé sur la date/heure
log_filename = datetime.now().strftime("logs/session_%Y-%m-%d_%H-%M-%S.log")

# Configuration du logger
logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger()
