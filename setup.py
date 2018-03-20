from setuptools import setup, find_packages
import platform


setup(
	name = 'dblayer',
	maintainer = 'IntegrCiTy development team',
	maintainer_email = 'edmund.widl@ait.ac.at',
	url = 'https://github.com/IntegrCiTy/dblayer',
	version = '0.0.1',
	platforms = [ platform.platform() ], # TODO indicate really tested platforms
	packages = find_packages(),
	install_requires = [ 'psycopg2', 'sqlalchemy' ],
	description = 'database persistency layer for OBNL',
	long_description = 'README.md',
	license = 'Apache License 2.0',
	keywords = [
		'CityGML',
		'Energy ADE',
		'Network Utility ADE',
		'Simulation Package' ],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Science/Research',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: Apache License 2.0',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3.6',
		'Topic :: Scientific/Engineering :: Energy Simulation' ],
)
