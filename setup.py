from setuptools import setup

setup(
    name = 'cabot-conf',
    version = '0.0.1',
    author = 'Scrunch Enterprises',
    author_email = 'andrew@scrunch.co',
    packages = ['cabot_conf'],
    url = 'https://github.com/andrewbaxter/cabot-conf',
    download_url = 'https://github.com/andrewbaxter/cabot-conf/tarball/v0.0.1',
    license = 'BSD',
    description = 'Use a JSON file to create Cabot instances, services, and checks.',
    long_description = open('readme.md', 'r').read(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
    ],
    install_requires = [
        'requests',
    ],
    entry_points = {
        'console_scripts': [
            'cabot_conf = cabot_conf.main:main',
        ],
    }
)
