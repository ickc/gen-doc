.PHONY: single_file
single_file: ../build/python-patterns.md
../build/python-patterns.md: build/python-patterns.md
		cp -f $< $@

.PHONY: all pdf html epub md
all: single_file pdf html epub md
pdf: build/python-patterns.pdf
html: build/python-patterns.html
epub: build/python-patterns.epub
md: build/python-patterns.md

build/python-patterns.pdf: git/_build/latex/PythonPatterns.pdf
	@mkdir -p build
	@cp -f $< $@
build/python-patterns.html: git/_build/singlehtml/index.html
	@mkdir -p build
	cp -f $< $@
# the epub output from Sphinx is invalid to parse by Apple Books
# Therefore we convert it again using ebook-convert
build/python-patterns.epub: git/_build/epub/PythonPatterns.epub
	@mkdir -p build
	ebook-convert $< $@ --title='Python Design Patterns' --authors='Brandon Rhodes' --language=en
build/python-patterns.md: git/_build/singlehtml/index.html
		pandoc -s -t gfm-raw_html -o $@ $<

git/_build/latex/PythonPatterns.pdf:
	cd git; $(MAKE) latexpdf
git/_build/singlehtml/index.html:
	cd git; $(MAKE) singlehtml
git/_build/epub/PythonPatterns.epub:
	cd git; $(MAKE) epub

.PHONY: clean Clean update
clean:
	rm -rf git/_build
Clean: clean
	rm -rf build
update:
	cd git; git pull
