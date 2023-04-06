# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

## [0.5.3] - 2023-05-02

### Added

- Now it's possible call PyASTrX in a watch mode. This mode will check the files every time they are modified. This is faster than calling PyASTrX every time you want to check the files.

- Treat YAML and Python files with syntax
errors.

- VsCode output to be used in the upcoming extension.

## [0.5.2] - 2023-10-01


### Fixed

- cache files are now stored with the original file extension followed by `.cache`. This fixes the issue
with two files with the same name but different extensions.

- Now it's possible to pass a list of different files mixing python and YAML files withouth any problem.

## [0.5.1] - 2023-08-01

### Fixed

- typing-extension is a requirement
- Check if there is any file to analyze
- allows to call pyastrx just for one specification:
```
$ pyastrx -s name_of_specification
```

## [0.5.0] - 2023-08-01

### Added

- Now it's possible to use PyASTrX to check and analyze YAML files.
- Specifications allow using multiple set of rules for different languages, files and folders.
- Added DBT case of use for YAML files.

### Changed

- Rules section should be inside a specification section

## [0.4.3] - 2022-9-10

### Fixed

- MyPy optional
- less command is now optional

## [0.4.2] - 2022-07-23


### Fixed

- (CVE-2022-2309) Upgrade lxml to 4.9.1 setup.py


## [0.4.1] - 2022-07-23


### Changed

- xpath expressions now is a key value pair in the configuration file

### Fixed

- (CVE-2022-2309) Upgrade lxml to 4.9.1 (requirements.in)


## [0.4.0] - 2022-06-13

### Added

- Mypy query command

```
$ mypyq filename.py
```

- Mypy type xml annotations
- Cache system

### Fixed

- Performance issues due the absence of caching

## [0.3.0] - 2022-06-02

### Added

- Pyre-query support (now is possible to create rules with type inference information)
- Export ast works with python 3.7
- Annotations

### Fixed

- The source code now is fully verified with mypy
- pep8
- removed redundant information (reduces mem consumption)

### Changed

- performance improvements (mem and cpu consumption)
- remove copyreg for multiprocessing.


## [0.2.0] - 2022-05-26
### Added

- Support for allow and deny lists
- Perf improvements using Xpath Evaluators
- Examples about how to use allow and deny lists
### Fixed

-
### Changed

- lxml extensions for xpath now can accept `match_params`

## [0.1.2] - 2022-05-25
### Added


### Fixed


### Changed

[Unreleased]: https://github.com/pyastrx/pyastrx/compare/0.5.3...main
[0.5.3]: https://github.com/pyastrx/pyastrx/compare/0.5.3...0.5.2
[0.5.2]: https://github.com/pyastrx/pyastrx/compare/0.5.2...0.5.1
[0.5.1]: https://github.com/pyastrx/pyastrx/compare/0.5.1...0.5.0
[0.5.0]: https://github.com/pyastrx/pyastrx/compare/0.5.0...0.4.3
[0.4.3]: https://github.com/pyastrx/pyastrx/compare/0.4.3...0.4.2
[0.4.2]: https://github.com/pyastrx/pyastrx/compare/0.4.2...0.4.1
[0.4.1]: https://github.com/pyastrx/pyastrx/compare/0.4.1...0.3.0
[0.4.0]: https://github.com/pyastrx/pyastrx/compare/0.3.0...0.2.0
[0.3.0]: https://github.com/pyastrx/pyastrx/compare/0.3.0...0.2.0
[0.2.0]: https://github.com/pyastrx/pyastrx/compare/0.2.0...0.1.2
[0.1.2]: https://github.com/pyastrx/pyastrx/compare/0.1.2...0.1.2
