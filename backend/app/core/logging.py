import logging
import sys
from typing import Any, Dict
from pathlib import Path

def setup_logging() -> logging.Logger:
    """Configure logging for the application"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("pdms_api")
    return logger

# Global logger instance
logger = setup_logging()

class LoggerMixin:
    """Mixin class to add logging capabilities"""
    
    @property
    def logger(self) -> logging.Logger:
        return logger
    
    def log_info(self, message: str, extra: Dict[str, Any] = None):
        """Log info message with optional extra data"""
        if extra:
            self.logger.info(f"{message} | Extra: {extra}")
        else:
            self.logger.info(message)
    
    def log_error(self, message: str, error: Exception = None):
        """Log error message with exception details"""
        if error:
            self.logger.error(f"{message} | Error: {str(error)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def log_warning(self, message: str, extra: Dict[str, Any] = None):
        """Log warning message"""
        if extra:
            self.logger.warning(f"{message} | Extra: {extra}")
        else:
            self.logger.warning(message)