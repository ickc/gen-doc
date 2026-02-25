DOMAIN = docs.isambard.ac.uk
URL = https://$(DOMAIN)/

HTML = $(shell find $(DOMAIN) -type f -iname '*.html')

.PHONY: single_file all
single_file: index.md
	mkdir -p ../build
	cp $< ../build/isambard-docs-html.md

all: single_file pandoc

args = -f html --file-scope
.PHONY: pandoc
pandoc: index.md index.html index.txt

index.md: $(HTML)
	pandoc $(args) -s -o $@ $^ -t gfm-raw_html

index.html: $(HTML)
	pandoc $(args) -s -o $@ $^ -t html

index.txt: $(HTML)
	pandoc $(args) -s -o $@ $^ -t plain

.PHONY: clean Clean update serve
clean:
	rm -f index.md index.html index.txt

Clean: clean
	rm -rf $(DOMAIN)

update:
	wget --mirror --convert-links --execute robots=off $(URL) || true

serve:
	cd $(DOMAIN); python -m http.server 9001 --bind 127.0.0.1
