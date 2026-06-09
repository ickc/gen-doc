PROJECT = conda-forge
GIT_DIR = git
PORT = 9000

PIXI_RUN = pixi run --manifest-path pixi.toml
GIT_PIXI_RUN = pixi run --manifest-path ../pixi.toml

SOURCE_FILES = $(shell find $(GIT_DIR)/docs $(GIT_DIR)/src $(GIT_DIR)/static $(GIT_DIR)/.ci_scripts -type f 2>/dev/null | sort)
ALL = index.html index.md index.txt

.PHONY: single_file all docs serve clean Clean update
single_file: index.md
	mkdir -p ../build
	cp $< ../build/$(PROJECT).md
all: $(ALL)
docs: $(GIT_DIR)/build/index.html

index.md: index.html
	$(PIXI_RUN) pandoc -s -f html -t gfm-raw_html --wrap=none --extract-media=media --resource-path=$(GIT_DIR)/build -o $@ $<
index.txt: index.html
	$(PIXI_RUN) pandoc -s -f html -t plain --wrap=none -o $@ $<
index.html: $(GIT_DIR)/build/index.html extract_docs.py
	$(PIXI_RUN) python extract_docs.py --source $(GIT_DIR) --build $(GIT_DIR)/build --out $@

$(GIT_DIR)/build/index.html: $(GIT_DIR)/node_modules/.package-lock.json $(SOURCE_FILES) $(GIT_DIR)/docusaurus.config.js
	cd $(GIT_DIR); $(GIT_PIXI_RUN) ./.ci_scripts/update_docs pre-build-only
	cd $(GIT_DIR); $(GIT_PIXI_RUN) npm run build

$(GIT_DIR)/node_modules/.package-lock.json: $(GIT_DIR)/package-lock.json $(GIT_DIR)/package.json pixi.lock
	cd $(GIT_DIR); $(GIT_PIXI_RUN) npm ci

serve: $(GIT_DIR)/build/index.html
	$(PIXI_RUN) python -m http.server $(PORT) --bind 127.0.0.1 --directory $(GIT_DIR)/build
clean:
	rm -f $(ALL)
	rm -rf media
	rm -rf $(GIT_DIR)/build $(GIT_DIR)/.docusaurus $(GIT_DIR)/static/schema
	rm -f $(GIT_DIR)/community/cfep-index.md $(GIT_DIR)/community/governance.md $(GIT_DIR)/community/code-of-conduct.md
Clean: clean
	rm -rf .pixi $(GIT_DIR)/node_modules
update:
	pixi update --manifest-path pixi.toml
	cd $(GIT_DIR); git checkout main; git pull origin main
print-%:
	$(info $* = $($*))
