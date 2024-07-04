PORT = 9001
DOMAIN = flox.dev
SUBDIR = docs
URL = https://$(DOMAIN)/$(SUBDIR)/

HTML = $(shell find $(DOMAIN)/$(SUBDIR) -type f -iname '*.html')

.PHONY: single_file all
single_file: index.md
	@echo "single file is ready at $$(realpath $<)"
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
Clean: clean
	rm -rf $(DOMAIN)
update:
	wget --mirror --convert-links --execute robots=off --include-directories=/docs $(URL)
serve:
	cd $(DOMAIN)/$(SUBDIR); python -m http.server $(PORT) --bind 127.0.0.1
print-%:
	$(info $* = $($*))
