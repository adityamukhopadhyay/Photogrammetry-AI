import logging
import logging.config
import os
from pathlib import Path

def configure_logger():
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Load configuration
    logging.config.fileConfig(
        "config/logging.conf",
        defaults={"LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")}
    )
    
    # Get both console and file loggers
    console_logger = logging.getLogger("root")
    file_logger = logging.getLogger("file_logger")
    
    # Add success level
    logging.SUCCESS = 25  # Between INFO and WARNING
    logging.addLevelName(logging.SUCCESS, 'SUCCESS')
    
    def success(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.SUCCESS):
            self._log(logging.SUCCESS, message, args, **kwargs)
    
    logging.Logger.success = success
    
    return file_logger  # Return file logger for consistency