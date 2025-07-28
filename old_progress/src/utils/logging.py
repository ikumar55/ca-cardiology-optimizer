"""
Logging configuration for the Cardiology Care Optimization System.

This module provides centralized logging setup for development, testing, and production
environments. It supports file logging, console output, and structured logging for
ML pipeline monitoring.
"""

import json
import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    use_structured: bool = False,
    component: Optional[str] = None,
) -> logging.Logger:
    """
    Set up logging configuration for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional specific log file name
        log_dir: Directory to store log files
        use_structured: Whether to use structured JSON logging
        component: Component name for structured logging (e.g., 'data_pipeline', 'gnn_training')

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Set default log file based on component or timestamp
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if component:
            log_file = f"{component}_{timestamp}.log"
        else:
            log_file = f"cardiology_optimizer_{timestamp}.log"

    log_file_path = log_path / log_file

    # Configure logging
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "structured": {
                "()": StructuredFormatter,
                "component": (
                    component if component is not None else "cardiology_optimizer"
                ),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "standard" if not use_structured else "structured",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "detailed" if not use_structured else "structured",
                "filename": str(log_file_path),
                "mode": "a",
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.FileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": str(log_path / "errors.log"),
                "mode": "a",
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "cardiology_optimizer": {
                "level": level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(config)
    return logging.getLogger("cardiology_optimizer")


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def __init__(self, component: str = "cardiology_optimizer"):
        super().__init__()
        self.component = component

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "component": self.component,
            "module": record.name,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_entry[key] = value

        return json.dumps(log_entry)


def get_component_logger(component: str, level: str = "INFO") -> logging.Logger:
    """
    Get a logger for a specific component.

    Args:
        component: Component name (e.g., 'data_pipeline', 'gnn_training', 'rl_training')
        level: Logging level

    Returns:
        Configured logger for the component
    """
    return setup_logging(level=level, component=component, use_structured=True)


def log_function_call(func):
    """Decorator to log function calls with parameters and execution time."""
    import functools
    import time

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("cardiology_optimizer")

        # Log function entry
        logger.debug(
            f"Entering {func.__name__} with args={str(args)}, kwargs={str(kwargs)}"
        )

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"Completed {func.__name__} in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Error in {func.__name__} after {execution_time:.3f}s: {str(e)}"
            )
            raise

    return wrapper


# Pre-configured loggers for common components
def get_data_logger() -> logging.Logger:
    """Get logger for data processing components."""
    return get_component_logger("data_pipeline", level="INFO")


def get_model_logger() -> logging.Logger:
    """Get logger for model training components."""
    return get_component_logger("model_training", level="INFO")


def get_dashboard_logger() -> logging.Logger:
    """Get logger for dashboard components."""
    return get_component_logger("dashboard", level="INFO")


def get_api_logger() -> logging.Logger:
    """Get logger for API components."""
    return get_component_logger("api", level="INFO")


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the specified module or component."""
    return get_component_logger(name, level="INFO")


# Environment-based configuration
def configure_for_environment(env: str = None) -> logging.Logger:
    """
    Configure logging based on environment.

    Args:
        env: Environment name ('development', 'testing', 'production')
             If None, reads from ENVIRONMENT variable or defaults to 'development'

    Returns:
        Configured logger
    """
    if env is None:
        env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        # Production: structured logging, WARNING level, separate error logs
        return setup_logging(
            level="WARNING",
            use_structured=True,
            log_dir=(
                "/var/log/cardiology_optimizer"
                if os.path.exists("/var/log")
                else "logs"
            ),
        )
    elif env == "testing":
        # Testing: minimal logging to avoid cluttering test output
        return setup_logging(level="ERROR", log_dir="test_logs")
    else:
        # Development: detailed logging with console output
        return setup_logging(level="DEBUG", use_structured=False)


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    logger = setup_logging(level="DEBUG", component="test")

    logger.info("Cardiology Optimizer logging system initialized")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    # Test component loggers
    data_logger = get_data_logger()
    data_logger.info("Data pipeline logger test")

    model_logger = get_model_logger()
    model_logger.info("Model training logger test")

    # Test decorator
    @log_function_call
    def example_function(x, y):
        return x + y

    result = example_function(5, 3)
    logger.info(f"Function result: {result}")
