import sys
import platform
from setuptools import setup


if platform.system() == 'Darwin':
    sys.exit("Error: zeus-server-load is not supported on macOS. Run the server on Windows or Linux.")

# Proceed with the setup
setup()
