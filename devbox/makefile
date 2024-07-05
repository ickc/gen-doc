# source md
PROJECT = devbox
DOC_ROOT = docs
FILES = $(shell find -L $(DOC_ROOT) -type f \( -name '*.mdx' -o -name '*.md' \) | sort --dictionary-order --ignore-case)

.PHONY: single_file all clean Clean update
single_file: index.md
	mkdir -p ../build
	cp $< ../build/$(PROJECT).md
all: single_file
clean:
	rm -rf index.md
Clean: clean
update:
	cd git; git checkout main; git pull origin main
print-%:
	$(info $* = $($*))

index.md: $(FILES)
	@: > $@
	@for file in $^; do \
		printf -- "---\nFrom %s\n\n" "$${file}" >> $@; \
		cat $$file >> $@; \
		echo '' >> $@; \
	done
