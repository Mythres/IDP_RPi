from setuptools import setup
setup(name='idp-rpi',
      version='1.0',
      py_modules=['idp_rpi'],
      entry_points={
          'console_scripts': [
            'idp-rpi = idp_rpi:blink'
	  ]
      },
)
