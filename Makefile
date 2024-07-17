export PROJECT := tuxlava
export TUXPKG_MIN_COVERAGE := 74
check: spellcheck stylecheck test

include $(shell tuxpkg get-makefile)

stylecheck: style flake8

spellcheck:
	codespell \
		--check-filenames \
		--skip '.git,public,dist,*.sw*,*.pyc,tags,*.json,.coverage,htmlcov,*.jinja2,*.yaml'
