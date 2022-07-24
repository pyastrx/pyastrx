"""."""

from setuptools import find_packages, setup

with open("README.rst", "r") as f:
    README_TEXT = f.read()

setup(
    name='pyastrx',
    version='0.4.2',
    long_description=README_TEXT,
    long_description_content_type="text/x-rst",
    description="'Simple projects are all alike; each complex"\
        +"project is complex in its own way.' - (adapted from Tolstoy's Anna Karenina)\n"\
        +"\nThe PyASTrX philosophy is to provide a simple, easy-to-use,"\
        +"and extensible framework for code quality analysis, refactoring"\
        +"and codebase analysis.",
    short_description="The PyASTrX philosophy is to provide a simple, easy-to-use,"\
        +"and extensible framework for code quality analysis, refactoring"\
        +"and codebase analysis.",
    license='MIT',
    install_requires=[
        'colorama==0.4.4', 'commonmark==0.9.1', 'gast==0.5.3', 'lxml==4.9.1',
        'prompt-toolkit==3.0.29', 'pyaml==21.10.1', 'pygments==2.12.0',
        'pyyaml==6.0', 'rich==12.4.1', 'wcwidth==0.2.5'],
    author='Bruno Messias',
    author_email='devmessias@gmail.com',
    url='https://github.com/pyastrx/pyastrx',
    entry_points={
        'console_scripts': [
            'pyastrx = pyastrx.frontend.cli:pyastrx',
            'mypyq = pyastrx.frontend.mypyq:mypy_query',
        ]
    },
    keywords=[
        "ast", "xpath", "yaml", "linter", "parser",
        "refactoring tool", "vscode", "pyre", "pyre-linter"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
    ],
    packages=find_packages()
)
