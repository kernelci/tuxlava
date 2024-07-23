export PROJECT := tuxlava
export TUXPKG_MIN_COVERAGE := 90
check: spellcheck stylecheck test

include $(shell tuxpkg get-makefile)

stylecheck: style flake8

spellcheck:
	codespell \
		-I codespell-ignore-list \
		--check-filenames \
		--skip '.git,public,dist,*.sw*,*.pyc,tags,*.json,.coverage,htmlcov,*.jinja2,*.yaml'
