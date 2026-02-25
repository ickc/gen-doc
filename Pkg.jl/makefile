VERSION=v1.12.3

single_file: Pkg.jl.pdf
	mkdir -p ../build
	cp $< ../build/Pkg.jl.pdf
Pkg.jl.pdf:
	wget "https://raw.githubusercontent.com/JuliaLang/Pkg.jl/gh-pages-pdf/${VERSION}/Pkg.jl.pdf"
all: single_file
clean:
Clean: clean
	rm -f Pkg.jl.pdf
update:
	url="$$(curl -sIL -o /dev/null -w "%{url_effective}\n" https://github.com/JuliaLang/Pkg.jl/releases/latest)"; \
	version="$${url##*/}"; \
	sed -i "s/^VERSION=.*/VERSION=$$version/" $(MAKEFILE_LIST)
