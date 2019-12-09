from setuptools import setup, find_packages


setup(
    name = 'dblayer',
    maintainer = 'IntegrCiTy development team',
    maintainer_email = 'edmund.widl@ait.ac.at',
    url = 'https://github.com/IntegrCiTy/dblayer',
    version = '1.0',
    platforms = [ 'any' ],
    packages = find_packages(),
    install_requires = [
        'sqlalchemy>=1.3.3',
        'psycopg2-binary>=2.8.2',
        'pygeoif>=0.7',
        'pandapower==1.6.1',
        'zerobnl @ git+https://github.com/IntegrCiTy/zerobnl@v1.0',
        'pandangas @ git+https://github.com/IntegrCiTy/PandaNGas.git@4202f42abd8fd2b1b17ae05fefdc042b092887f7',
        'pandathermal @ git+https://github.com/IntegrCiTy/PandaThermal.git@6b08ca6c600f742624837b898b5a74a69ebea682',
    ],
    description = 'Data Access Layer for the IntegrCiTy toolchain',
    long_description = 'README.md',
    license = 'BSD 2-Clause License',
    keywords = [
	'CityGML',
	'Energy ADE',
	'Network Utility ADE',
	'Simulation Package'
    ],
    classifiers = [
	'Development Status :: 4 - Beta',
	'Environment :: Console',
	'Intended Audience :: Science/Research',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: BSD License',
	'Natural Language :: English',
	'Operating System :: OS Independent',
	'Programming Language :: Python :: 3.6',
	'Topic :: Scientific/Engineering :: Energy Simulation'
    ],
)
