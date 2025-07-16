.PHONY: single_file

single_file: ../build/GW4-Isambard.md
../build/GW4-Isambard.md: build/GW4-Isambard.md
		cp -f $< $@

.PHONY: all pdf html epub md
all: single_file pdf html epub md
pdf: build/GW4-Isambard.pdf
html: build/GW4-Isambard.html
epub: build/GW4-Isambard.epub
md: build/GW4-Isambard.md

build/GW4-Isambard.pdf: git/_build/latex/GW4-Isambard.pdf
	@mkdir -p build
	@cp -f $< $@
build/GW4-Isambard.html: git/_build/singlehtml/index.html
	@mkdir -p build
	cp -f $< $@
build/GW4-Isambard.epub: git/_build/epub/GW4-Isambard.epub
	@mkdir -p build
	cp -f $< $@
build/GW4-Isambard.md: git/_build/singlehtml/index.html
	@mkdir -p build
	pandoc -s -t gfm-raw_html -o $@ $<

git/_build/latex/GW4-Isambard.pdf:
	cd git; pixi run $(MAKE) latexpdf SPHINXOPTS='-D latex_engine=lualatex'
git/_build/singlehtml/index.html:
	cd git; pixi run $(MAKE) singlehtml
git/_build/epub/GW4-Isambard.epub:
	cd git; pixi run $(MAKE) epub

.PHONY: clean Clean update
clean:
	rm -rf git/_build
Clean: clean
	rm -rf build
update:
	cd git; git checkout master; git pull origin master
