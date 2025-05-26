import logging
import time

logging.getLogger("multipart").setLevel(logging.WARNING)

logging.Formatter.converter = time.gmtime
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)
