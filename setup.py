from setuptools import setup, find_packages
setup(
  name = 'bsl_inst',         # How you named your package folder (MyLib)
  packages = find_packages(),   # Chose the same as "name"
  version = '0.17',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Universal Instrument Control for BioSensors Lab @ UIUC',   # Give a short description about your library
  author = 'Zhongmin Zhu',                   # Type in your name
  author_email = 'j@metadata.cc',      # Type in your E-Mail
  url = 'https://github.com/BioSensorsLab-Illinois/bsl_inst_control',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/BioSensorsLab-Illinois/bsl_inst_control/archive/refs/tags/Testing.tar.gz',    # I explain this later on
  keywords = ['BSL', 'Instrument', 'UIUC'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'loguru',
          'numpy',
          'pyserial',
          'pyvisa',
          'pyvisa-py',
          'seabreeze',
          'libusb',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
  ],
)