export PROJECT := tuxlava
export TUXPKG_MIN_COVERAGE := 90
export TUXPKG_FLAKE8_OPTIONS := "--exclude=site-packages"
check: spellcheck stylecheck test

include $(shell tuxpkg get-makefile)

.PHONY: tags

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

tags:
	ctags -R $(PROJECT)/ test/
