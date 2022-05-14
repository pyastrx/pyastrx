install-pip-tools:
	python3 -m pip install pip-tools

pip-compile: install-pip-tools
	pip-compile --no-emit-index-url requirements.in
	pip-compile --no-emit-index-url requirements_dev.in


## @category Dev-build
## Install all the dev dependencies
install-dev:
	pip install -r requirements_dev.txt
	pip install -r requirements.txt
	pre-commit install
	python3 setup.py develop


## @category Dev-build
## Search for all the dependencies and install them
sync-env: pip-compile
	pip-sync requirements.txt requirements_dev.txt
	python3 setup.py develop

## @category Dev-Code Quality
## Run all the tests
test:
	pytest -svv tests

## @category Dev-Code Quality
## Linter  
linter:
	flake8 pyastsearch

## @category Dev-Code Quality
## reformat code through black
reformat:
	black pyastsearch

## @category Dev-Code Quality
pre-commit:
	pre-commit run --all-files

## @category Users
## Install
install:
	pip install -r requirements.txt
	python3 setup.py develop



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################
.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
# fancy colors
RULE_COLOR := "$$(tput setaf 6)"
VARIABLE_COLOR = "$$(tput setaf 2)"
VALUE_COLOR = "$$(tput setaf 1)"
CLEAR_STYLE := "$$(tput sgr0)"
TARGET_STYLED_HELP_NAME = "$(RULE_COLOR)TARGET$(CLEAR_STYLE)"
ARGUMENTS_HELP_NAME = "$(VARIABLE_COLOR)ARGUMENT$(CLEAR_STYLE)=$(VALUE_COLOR)VALUE$(CLEAR_STYLE)"

# search regex
target_regex = [a-zA-Z0-9%_\/%-]+
variable_regex = [^:=\s ]+
variable_assignment_regex = \s*:?[+:!\?]?=\s*
value_regex = .*
category_annotation_regex = @category\s+
category_regex = [^<]+

# tags used to delimit each parts
target_tag_start = "\<target-definition\>"
target_tag_end = "\<\\\/target-definition\>"
target_variable_tag_start = "\<target-variable\>"
target_variable_tag_end = "\<\\\/target-variable\>"
variable_tag_start = "\<variable\>"
variable_tag_end = "\<\\\/variable\>"
global_variable_tag_start = "\<global-variable\>"
global_variable_tag_end = "\<\\\/global-variable\>"
value_tag_start = "\<value\>"
value_tag_end = "\<\\\/value\>"
prerequisites_tag_start = "\<prerequisites\>"
prerequisites_tag_end = "\<\\\/prerequisites\>"
doc_tag_start = "\<doc\>"
doc_tag_end = "\<\\\/doc\>"
category_tag_start = "\<category-other\>"
category_tag_end = "\<\\\/category-other\>"
default_category_tag_start = "\<category-default\>"
default_category_tag_end = "\<\\\/category-default\>"

DEFAULT_CATEGORY = Targets and Arguments

## @category Help
## all targets available
help:
	@echo "Usage: make [$(TARGET_STYLED_HELP_NAME) [$(TARGET_STYLED_HELP_NAME) ...]] [$(ARGUMENTS_HELP_NAME) [$(ARGUMENTS_HELP_NAME) ...]]"
	@sed -n -e "/^## / { \
		h; \
		s/.*/##/; \
		:doc" \
		-E -e "H; \
		n; \
		s/^##\s*(.*)/$(doc_tag_start)\1$(doc_tag_end)/; \
		t doc" \
		-e "s/\s*#[^#].*//; " \
		-E -e "s/^(define\s*)?($(variable_regex))$(variable_assignment_regex)($(value_regex))/$(global_variable_tag_start)\2$(global_variable_tag_end)$(value_tag_start)\3$(value_tag_end)/;" \
		-E -e "s/^($(target_regex))\s*:?:\s*(($(variable_regex))$(variable_assignment_regex)($(value_regex)))/$(target_variable_tag_start)\1$(target_variable_tag_end)$(variable_tag_start)\3$(variable_tag_end)$(value_tag_start)\4$(value_tag_end)/;" \
		-E -e "s/^($(target_regex))\s*:?:\s*($(target_regex)(\s*$(target_regex))*)?/$(target_tag_start)\1$(target_tag_end)$(prerequisites_tag_start)\2$(prerequisites_tag_end)/;" \
		-E -e " \
		G; \
		s/##\s*(.*)\s*##/$(doc_tag_start)\1$(doc_tag_end)/; \
		s/\\n//g;" \
		-E -e "/$(category_annotation_regex)/!s/.*/$(default_category_tag_start)$(DEFAULT_CATEGORY)$(default_category_tag_end)&/" \
		-E -e "s/^(.*)$(doc_tag_start)$(category_annotation_regex)($(category_regex))$(doc_tag_end)/$(category_tag_start)\2$(category_tag_end)\1/" \
		-e "p; \
	}"  ${MAKEFILE_LIST} \
	| sort  \
	| sed -n \
		-e "s/$(default_category_tag_start)/$(category_tag_start)/" \
		-e "s/$(default_category_tag_end)/$(category_tag_end)/" \
		-E -e "{G; s/($(category_tag_start)$(category_regex)$(category_tag_end))(.*)\n\1/\2/; s/\n.*//; H; }" \
		-e "s/$(category_tag_start)//" \
		-e "s/$(category_tag_end)/:\n/" \
		-e "s/$(target_variable_tag_start)/$(target_tag_start)/" \
		-e "s/$(target_variable_tag_end)/$(target_tag_end)/" \
		-e "s/$(target_tag_start)/    $(RULE_COLOR)/" \
		-e "s/$(target_tag_end)/$(CLEAR_STYLE) /" \
		-e "s/$(prerequisites_tag_start)$(prerequisites_tag_end)//" \
		-e "s/$(prerequisites_tag_start)/[/" \
		-e "s/$(prerequisites_tag_end)/]/" \
		-E -e "s/$(variable_tag_start)/$(VARIABLE_COLOR)/g" \
		-E -e "s/$(variable_tag_end)/$(CLEAR_STYLE)/" \
		-E -e "s/$(global_variable_tag_start)/    $(VARIABLE_COLOR)/g" \
		-E -e "s/$(global_variable_tag_end)/$(CLEAR_STYLE)/" \
		-e "s/$(value_tag_start)/ (default: $(VALUE_COLOR)/" \
		-e "s/$(value_tag_end)/$(CLEAR_STYLE))/" \
		-e "s/$(doc_tag_start)/\n        /g" \
		-e "s/$(doc_tag_end)//g" \
		-e "p"
