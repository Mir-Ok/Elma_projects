from environs import Env
from loguru import logger


logger = logger


env = Env()
env.read_env()

# environment
ELMA_TOKEN = env("ELMA_TOKEN")
ELMA_STAND = env("ELMA_STAND")
ELMA_DIRECTORY = env("ELMA_DIRECTORY")

# ELMA_TOKEN = 'a3e289f3-65c4-4601-bff3-e86a3dfd1baf'
# ELMA_STAND = 'https://idpo.proactor.pro/'
# ELMA_DIRECTORY = 'f942bd82-c21c-4de2-94fd-f2715a5e9941'
