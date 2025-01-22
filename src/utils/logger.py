import logging
import logging.config
import os
from pathlib import Path

def configure_logger():
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    logging.config.fileConfig(
        "config/logging.conf",
        defaults={"LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")}
    )
    return logging.getLogger(__name__)