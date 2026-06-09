PROJECT = flox
GIT_DIR = git

PIXI_RUN = pixi run --manifest-path pixi.toml
GIT_PIXI_RUN = pixi run --manifest-path ../pixi.toml

FLOX_VERSION_FILE = $(GIT_DIR)/FLOX_VERSION
MAN_PAGES_STAMP = $(GIT_DIR)/docs/man/.generated-stamp
POETRY_STAMP = .poetry-install-stamp

SOURCE_FILES = $(shell find $(GIT_DIR)/docs $(GIT_DIR)/overrides $(GIT_DIR)/mkdocs.yml $(GIT_DIR)/pyproject.toml $(GIT_DIR)/poetry.lock $(GIT_DIR)/mkdocs_material-9.5.10+insiders.4.52.2.tar.gz -type f ! -path '$(GIT_DIR)/docs/man/*' 2>/dev/null | sort)
ALL = index.html index.md index.txt

.PHONY: single_file all docs serve clean Clean update print-%
single_file: index.md
	mkdir -p ../build
	cp $< ../build/$(PROJECT).md
all: single_file $(ALL)
docs: $(GIT_DIR)/site/index.html

index.md: index.html
	$(PIXI_RUN) pandoc -s -f html -t gfm-raw_html --wrap=none --extract-media=media --resource-path=$(GIT_DIR)/site -o $@ $<
index.txt: index.html
	$(PIXI_RUN) pandoc -s -f html -t plain --wrap=none -o $@ $<
index.html: $(GIT_DIR)/site/index.html extract_docs.py
	$(PIXI_RUN) python extract_docs.py --source $(GIT_DIR) --build $(GIT_DIR)/site --version-file $(FLOX_VERSION_FILE) --out $@

$(GIT_DIR)/site/index.html: $(POETRY_STAMP) $(MAN_PAGES_STAMP) $(SOURCE_FILES)
	cd $(GIT_DIR); FLOX_VERSION="$$(cat FLOX_VERSION)" DISABLE_MKDOCS_2_WARNING=true POETRY_VIRTUALENVS_IN_PROJECT=true $(GIT_PIXI_RUN) poetry run mkdocs build

$(POETRY_STAMP): pixi.lock pixi.toml $(GIT_DIR)/pyproject.toml $(GIT_DIR)/poetry.lock $(GIT_DIR)/mkdocs_material-9.5.10+insiders.4.52.2.tar.gz
	cd $(GIT_DIR); POETRY_VIRTUALENVS_IN_PROJECT=true $(GIT_PIXI_RUN) poetry install --quiet
	touch $@

$(MAN_PAGES_STAMP): generate_man_pages.py pixi.lock pixi.toml | $(POETRY_STAMP)
	$(PIXI_RUN) python generate_man_pages.py --source $(GIT_DIR) --cache $(GIT_DIR)/.cache/gen-doc --version-file $(FLOX_VERSION_FILE) --stamp $@

serve: $(GIT_DIR)/site/index.html
	$(PIXI_RUN) python -m http.server 9000 --bind 127.0.0.1 --directory $(GIT_DIR)/site
clean:
	rm -f $(ALL)
	rm -rf media
	rm -rf $(GIT_DIR)/site $(GIT_DIR)/docs/man
Clean: clean
	rm -rf .pixi $(POETRY_STAMP) $(GIT_DIR)/.cache/gen-doc $(FLOX_VERSION_FILE)
update:
	pixi update --manifest-path pixi.toml
	cd git; git checkout main; git pull origin main
	rm -f $(FLOX_VERSION_FILE) $(MAN_PAGES_STAMP)
print-%:
	$(info $* = $($*))
