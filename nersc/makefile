# source md
MKDOCS_YML = git/mkdocs.yml
REL_FILES = $(shell pixi run ./parse_mkdocs.py filename $(MKDOCS_YML))
FILES = $(patsubst %,docs/%,$(REL_FILES))

# serves
PORT = 9000

ALL = index.md index.markdown index.txt mkdocs.yml public/print_page/index.html

.PHONY: single_file all
# choose the best single file format here
single_file: public/print_page/index.html
	@echo "single file is ready at $$(realpath $<)"
all: $(ALL)

# simple concat target
index.md: $(MKDOCS_YML) $(FILES)
	pixi run ./parse_mkdocs.py concat $< -d docs -o $@

# heavy lifting by pandoc
.PHONY: pandoc
pandoc: index.markdown index.txt
# this one just interpret the markdown by pandoc which doesn't work
# as they have different markdown extensions
# args = -f commonmark_x+rebase_relative_paths --file-scope --pdf-engine=xelatex
# index.markdown: $(FILES)
# 	pandoc $(args) -o $@ $^
# index.pdf: $(FILES)
# 	pandoc $(args) -o $@ $^
index.markdown: public/print_page/index.html
	cd $(<D); pixi run pandoc -s -o ../../$@ $(<F) -t gfm-raw_html
index.txt: public/print_page/index.html
	cd $(<D); pixi run pandoc -s -o ../../$@ $(<F) -t plain

# directly using mkdocs by upstream
mkdocs.yml: $(MKDOCS_YML)
	cp $< $@
	echo '  - print-site' >> $@
.PHONY: docs
docs: public/print_page/index.html
public/print_page/index.html: mkdocs.yml $(FILES)
	pixi run mkdocs build

# misc
.PHONY: serve clean format
serve:
	cd public; pixi run python -m http.server $(PORT) --bind 127.0.0.1
clean:
	rm -f $(ALL)
	rm -rf public
format:
	autoflake --in-place --recursive --expand-star-imports --remove-all-unused-imports --ignore-init-module-imports --remove-duplicate-keys --remove-unused-variables parse_mkdocs.py
	black parse_mkdocs.py
	isort parse_mkdocs.py
update:
	pixi update
print-%:
	$(info $* = $($*))
