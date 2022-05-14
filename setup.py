"""Setup for astpath, adds astpath console_script."""

from setuptools import setup

setup(
    name='pyastsearch',
    packages=['pyastsearch'],
    version='0.0.1',
    description='based on H. Chase Stevens idea',
    license='MIT',
    author='Bruno Messias',
    author_email='devmessias@gmail.com',
    url='',
    extras_require={
        'xpath': ['lxml>=3.3.5', ]
    },
    entry_points={
        'console_scripts': [
            'pyastsearch = pyastsearch.cli:main',
            'pyxpathlinter = pyastsearch.cli:main',

        ]
    },
    keywords='xpath xml ast asts syntax query',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
    ]
)
