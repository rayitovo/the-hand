# utils/logger.py
import logging
import config  # Import your config.py file

def setup_logger(log_level=config.LOG_LEVEL):
    """Sets up a basic logger."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__) # Or you can use a more specific name

logger = setup_logger() # Initialize the logger

if __name__ == '__main__':
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")