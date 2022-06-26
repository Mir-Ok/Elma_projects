from environs import Env
from loguru import logger

logger = logger

env = Env()
env.read_env()

# environment
ELMA_TOKEN = env("ELMA_TOKEN")
ELMA_STAND = env("ELMA_STAND")
ELMA_ZIP_DIRECTORY = env("ELMA_ZIP_DIRECTORY")
ELMA_PDF_DIRECTORY = env("ELMA_PDF_DIRECTORY")
ELMA_QR_DIRECTORY = env("ELMA_QR_DIRECTORY")


SUFFIX_LIST = {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif', 'pdf'}
