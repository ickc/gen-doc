PROJECT = isambard-docs
GIT_DIR = git
DOC_ROOT = $(GIT_DIR)/docs
MKDOCS_YML = $(GIT_DIR)/mkdocs.yml
PIXI_RUN = pixi run --manifest-path pixi.toml

HAVE_SUBMODULE = $(shell git -C $(GIT_DIR) rev-parse --is-inside-work-tree >/dev/null 2>&1 && echo yes)

.PHONY: single_file all clean Clean update serve print-%

ifeq ($(HAVE_SUBMODULE),yes)
FILES = $(shell find -L $(DOC_ROOT) -type f -name '*.md' | sort --dictionary-order --ignore-case)
ALL = index.markdown index.txt mkdocs.yml site/print_page/index.html
PYTHON_DEPS = .pixi/requirements-installed

single_file: index.markdown
	mkdir -p ../build
	cp $< ../build/$(PROJECT).md

all: single_file $(ALL)

mkdocs.yml: $(MKDOCS_YML) makefile
	awk 'in_plugins && /^[^[:space:]][^:]*:/ { if (!has_print) print "    - print-site"; in_plugins = 0 } /^site_url:/ { print; print "docs_dir: git/docs"; next } /^[[:space:]]+custom_dir: overrides/ { sub("overrides", "git/overrides") } /^plugins:/ { in_plugins = 1 } in_plugins && /^[[:space:]]+-[[:space:]]+print-site/ { has_print = 1 } { print } END { if (in_plugins && !has_print) print "    - print-site" }' $< > $@

$(PYTHON_DEPS): makefile pixi.toml $(GIT_DIR)/requirements.txt $(GIT_DIR)/extra_python/pyproject.toml
	cd $(GIT_DIR); pixi run --manifest-path ../pixi.toml python -m pip install --requirement requirements.txt mkdocs-print-site-plugin
	mkdir -p $(@D)
	touch $@

site/print_page/index.html: mkdocs.yml $(PYTHON_DEPS) $(FILES)
	$(PIXI_RUN) mkdocs build

index.markdown: site/print_page/index.html
	$(PIXI_RUN) pandoc -s -o $@ $< -t gfm-raw_html --extract-media=media --resource-path=site/print_page

index.txt: site/print_page/index.html
	$(PIXI_RUN) pandoc -s -o $@ $< -t plain

serve: site/print_page/index.html
	$(PIXI_RUN) python -m http.server 9000 --directory site --bind 127.0.0.1

clean:
	rm -f index.markdown index.txt mkdocs.yml
	rm -rf site

Clean: clean
	rm -rf .pixi

update:
	cd $(GIT_DIR); git checkout main; git pull origin main
	rm -f $(PYTHON_DEPS)

else
single_file all update:
	@echo "Skipping $(PROJECT): private submodule $(GIT_DIR) is not initialized"

clean:
	rm -f index.markdown index.txt mkdocs.yml
	rm -rf site

Clean: clean
	rm -rf .pixi
endif

print-%:
	$(info $* = $($*))
