# source md
MKDOCS_YML = git/mkdocs.yml
FILES = $(patsubst %,docs/%,$(REL_FILES))

# serves
PORT = 9000

ALL = index.markdown index.txt mkdocs.yml site/print_page/index.html

.PHONY: single_file all
# choose the best single file format here
single_file: index.markdown
	mkdir -p ../build
	cp $< ../build/pixi.md
all: $(ALL)

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
index.markdown: site/print_page/index.html
	cd $(<D); pixi run pandoc -s -o ../../$@ $(<F) -t gfm-raw_html
index.txt: site/print_page/index.html
	cd $(<D); pixi run pandoc -s -o ../../$@ $(<F) -t plain

# directly using mkdocs by upstream
mkdocs.yml: $(MKDOCS_YML)
	cp $< $@
	echo '  - print-site' >> $@
.PHONY: docs
docs: site/print_page/index.html
site/print_page/index.html: mkdocs.yml $(FILES)
	pixi run mkdocs build

# misc
.PHONY: serve clean Clean update
serve:
	cd site; pixi run python -m http.server $(PORT) --bind 127.0.0.1
clean:
	rm -f $(ALL)
	rm -rf site
Clean: clean
	rm -rf .pixi
update:
	pixi update
	cd git; git checkout main; git pull origin main
print-%:
	$(info $* = $($*))
