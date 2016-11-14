
from setuptools import setup

VERSION='0.1'

setup(
    name='brewgear-pi',
    version=VERSION,
    description='Home brewing automation with Raspberry Pi',
    author="Arjan J. Molenaar",

    setup_requires = [
        'nose >= 0.10.4',
        'setuptools-git >= 0.3.4',
        'pytest-runner'
    ],
    tests_require=[
        'pytest'
    ]
    )

# vim:sw=4:et:ai
