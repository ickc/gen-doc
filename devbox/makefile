PROJECT = devbox
GIT_DIR = git

PIXI_RUN = pixi run --manifest-path pixi.toml
GIT_PIXI_RUN = pixi run --manifest-path ../pixi.toml

SOURCE_FILES = $(shell find $(GIT_DIR)/docs/devbox $(GIT_DIR)/docs.json $(GIT_DIR)/package.json $(GIT_DIR)/pnpm-lock.yaml -type f 2>/dev/null | sort)
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
index.html: extract_docs.py $(GIT_DIR)/node_modules/.modules.yaml $(SOURCE_FILES)
	$(PIXI_RUN) python extract_docs.py --source $(GIT_DIR) --out $@

$(GIT_DIR)/node_modules/.modules.yaml: $(GIT_DIR)/package.json $(GIT_DIR)/pnpm-lock.yaml pixi.lock
	cd $(GIT_DIR); $(GIT_PIXI_RUN) pnpm install --frozen-lockfile

serve: index.html
	$(PIXI_RUN) python -m http.server 9000 --bind 127.0.0.1
clean:
	rm -f $(ALL)
	rm -rf media
Clean: clean
	rm -rf .pixi $(GIT_DIR)/node_modules
update:
	pixi update --manifest-path pixi.toml
	cd git; git checkout main; git pull origin main
print-%:
	$(info $* = $($*))
