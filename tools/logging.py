
import logging


def setup_logging(level: str = 'INFO'):
    # Set logging level
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
