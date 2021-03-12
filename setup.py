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
        'fluids>=0.1.75',
        'networkx>=2.4',
        'pandapower==1.6.1',
        'pandas>=0.25.3',
        'psycopg2-binary>=2.8.2',
        'pygeoif>=0.7',
        'sqlalchemy>=1.3.3',
        'thermo>=0.1.39',
        'zerobnl @ git+https://github.com/IntegrCiTy/zerobnl@v1.1',
        'pandangas @ git+https://github.com/IntegrCiTy/PandaNGas.git@dd16c9f1a753de03207bbc7d7e9a41a3fba99656',
        'pandathermal @ git+https://github.com/IntegrCiTy/PandaThermal.git@55afee02dff4ac1288d0abef4bdc9ea44f02d632',
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
