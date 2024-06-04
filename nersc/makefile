REL_FILES = $(shell ./parse_mkdocs.py git/mkdocs.yml)
FILES = $(patsubst %,git/docs/%,$(REL_FILES))
args =  -f commonmark_x+rebase_relative_paths --file-scope --pdf-engine=xelatex

all: README.md README.markdown README.pdf

README.md: $(FILES)
	cat $^ > $@
README.markdown: $(FILES)
	pandoc $(args) -o $@ $^
README.pdf: $(FILES)
	pandoc $(args) -o $@ $^

print-%:
	$(info $* = $($*))
