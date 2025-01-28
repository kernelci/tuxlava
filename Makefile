export PROJECT := tuxlava
export TUXPKG_MIN_COVERAGE := 95
export TUXPKG_FLAKE8_OPTIONS := "--exclude=site-packages"
check: spellcheck stylecheck test

include $(shell tuxpkg get-makefile)

.PHONY: tags

help:
	@echo 'Possible targets:'
	@echo ''
	@echo '  doc          - Build documentation'
	@echo '  stylecheck   - Check code style'
	@echo '  spellcheck   - Check code spelling'
	@echo '  tags         - Generate an index file of the surce and test code (ctags)'
	@echo '  test         - Run unit tests'

stylecheck: style flake8

spellcheck:
	codespell \
		-I codespell-ignore-list \
		--check-filenames \
		--skip '.git,public,dist,*.sw*,*.pyc,tags,*.json,.coverage,htmlcov,*.jinja2,*.yaml'

doc: docs/index.md
	mkdocs build

docs/index.md: README.md scripts/readme2index.sh
	scripts/readme2index.sh $@

doc-serve:
	mkdocs serve

lava-validate:
	python3 test/validate.py

tags:
	ctags -R $(PROJECT)/ test/
