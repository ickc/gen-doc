PROJECT = flox
GIT_DIR = git

PIXI_RUN = pixi run --manifest-path pixi.toml
MINT_COMMAND = ../node_modules/.bin/mint

SOURCE_FILES = $(shell find $(GIT_DIR) -type f \( -name '*.mdx' -o -name 'docs.json' -o -path '$(GIT_DIR)/images/*' -o -path '$(GIT_DIR)/logo/*' -o -name 'favicon.ico' -o -name 'favicon.svg' -o -name 'FLOX_VERSION' \) 2>/dev/null | sort)
ALL = index.html index.md index.txt

.PHONY: single_file all docs serve clean Clean update print-%
single_file: index.md
	mkdir -p ../build
	cp $< ../build/$(PROJECT).md
all: single_file $(ALL)
docs: index.html

index.md: index.html
	$(PIXI_RUN) pandoc -s -f html -t gfm-raw_html --wrap=none --extract-media=media --resource-path=$(GIT_DIR) -o $@ $<
index.txt: index.html
	$(PIXI_RUN) pandoc -s -f html -t plain --wrap=none -o $@ $<
index.html: extract_docs.py node_modules/.package-lock.json $(SOURCE_FILES)
	$(PIXI_RUN) python extract_docs.py --source $(GIT_DIR) --mint-command "$(MINT_COMMAND)" --out $@

node_modules/.package-lock.json: package-lock.json package.json pixi.lock
	PUPPETEER_SKIP_DOWNLOAD=true $(PIXI_RUN) npm ci

serve: index.html
	$(PIXI_RUN) python -m http.server 9000 --bind 127.0.0.1
clean:
	rm -f $(ALL)
	rm -rf media
Clean: clean
	rm -rf .pixi node_modules
update:
	pixi update --manifest-path pixi.toml
	cd $(GIT_DIR); git checkout main; git pull origin main
print-%:
	$(info $* = $($*))
