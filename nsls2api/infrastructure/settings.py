from starlette.config import Config
from starlette.datastructures import URL, Secret, CommaSeparatedStrings

config = Config(".env")

# PASS Production
PASS_API_KEY = config('PASS_API_KEY', cast=Secret)
PASS_API_URL = config('PASS_API_URL', cast=URL, default="https://passservices.bnl.gov/passapi")

# N2SNUserTools
ACTIVE_DIRECTORY_SERVER = config('ACTIVE_DIRECTORY_SERVER', cast=str)
ACTIVE_DIRECTORY_SERVER_LIST = config('ACTIVE_DIRECTORY_SERVER_LIST')
N2SN_USER_SEARCH = config('N2SN_USER_SEARCH')
N2SN_GROUP_SEARCH = config('N2SN_GROUP_SEARCH')
BNLROOT_CA_CERTS_FILE = config('BNLROOT_CA_CERTS_FILE', cast=str)

# MongoDB
#NSLS2CORE_MONGODB_URI = config('NSLS2CORE_MONGODB_URI', cast=str)