This builds single file targets from documentations, primarily for the purpose of feeding into LLMs to chat with doc.

# Getting started

The normal update target initializes and updates the public submodules:

```bash
make update
```

After that, build the available single-file documentation targets:

```bash
make single_file
```

Some documentation sources are optional private submodules.
They are marked with `update = none` in `.gitmodules`, so `make update` skips their initial clone.
This lets users without access update the public submodules and build the public documentation without Git trying to clone private repositories.

For a fresh checkout where you also have access to the private submodules, run both update targets:

```bash
make update update-private
```

`make update-private` only initializes and updates the optional private submodules.
It does not replace `make update`, because it does not initialize or update the public submodules.
The two targets are independent and complementary; the combined command above runs the public update first, then the private update.

After a private submodule has been initialized once, the regular `make update` target will also run that project's own `update` target.
Run `make update-private` again when you are setting up a fresh checkout, when a private submodule was not initialized before, or when you specifically want to refresh only the optional private submodules.

# Notes

The root `build/` directory, when present, is aggregate output.
Every other first-level project directory is its own documentation project.
Within each project, it must contain

- `makefile` with targets `single_file`, `all`, `clean`, `Clean`, `update`.

    - `single_file` should make the best single file target, and make a copy at `build/` with the name of that subdirectory and an appropriate extension.

    - `all` make all single file targets, including `single_file` and optionally other alternative single file targets.

    - `clean` cleanup generated files.

    - `Clean` is a more thorough cleanup, including other things that are more expensive to generate such as the environment.

    - `update` will update the doc to point to the latest one, and also the environment if present.

- `.gitignore`

- optionally `README.md`

# Tips and examples

Some patterns in creating single file documentations are discussed below.

## Submodules

Usually we are manipulating from the source of a repository. In that case, add it as a submodule to track it first:

```bash
git submodule add URL PROJECT/git
```

## Environments

Usually the environment to build a doc is non-trivial. In that case, a reproducible environment should be included, such as via pixi.

In some cases, tools involve is commonly available on UNIX and hence a custom environment is not created.

## Patterns

Current projects:

| Project | Pattern | Source | Environment | Primary single file |
| --- | --- | --- | --- | --- |
| `conda-forge` | Build, extract & convert | public submodule, Docusaurus | pixi + npm | Markdown |
| `devbox` | Build, serve, crawl, extract & convert | public submodule, Mintlify | pixi + pnpm | Markdown |
| `flox` | Simply concat | public submodule, Markdown | system tools | Markdown |
| `isambard-docs` | Tweak & rebuild | optional private submodule, MkDocs | pixi | Markdown |
| `mamba` | Simply build | public submodule, Sphinx + Doxygen | pixi | Markdown |
| `nersc` | Tweak & rebuild | public submodule, MkDocs | pixi | Markdown |
| `pandoc` | Simply Download | release artifact | system tools | Markdown |
| `pixi` | Tweak & rebuild | public submodule, MkDocs | pixi | Markdown |
| `Pkg.jl` | Simply Download | release artifact | system tools | PDF |
| `python-patterns` | Simply build | public submodule, Sphinx | pixi | Markdown |
| `spack` | Simply build | public submodule, Sphinx | pixi | plain text |

### Simply Download

Examples: `pandoc`, `Pkg.jl`

### Simply concat

In some cases, the documentation framework used in a project does not have an option to produce single file documentation. We will then simply concat all relevant doc files and call it a day.

Examples: `flox`

### Crawl & concat

Some projects do not provide the source of documentation, or the source is not available locally.
We use this recipe instead:

1. crawl by wget
2. convert to markdown by pandoc
3. concat

Previous example: [`flox`](https://github.com/ickc/gen-doc/blob/416d3a941537cd767a63900b3dde5f72ba0f82c6/flox/makefile)

### Simply build

We will use the original build system to produce a single file target that is not provided.

Examples: `python-patterns`, `spack`, `mamba` with sphinx

### Tweak & rebuild

We would dive into the doc build framework and tweak it so that single file target are produced.

Examples:

- `nersc`, `pixi`, `isambard-docs` with MkDocs and additional plugin `print-site`

### Build, extract & convert

Some documentation sites can build a complete HTML site, but the built site is split across routes and contains navigation or generated pages we do not want verbatim.
We build the upstream site, extract the documentation body into one HTML file, then convert that file to Markdown or plain text with pandoc.

Examples: `conda-forge` with Docusaurus

### Build, serve, crawl, extract & convert

Some documentation frameworks do not expose a static build artifact or a single-file output, but they can serve a rendered local preview.
In that case, we use the upstream source to start a local preview server, crawl the rendered routes from that server, extract the documentation body from each page, combine the extracted bodies into one HTML file, then convert that file to Markdown or plain text with pandoc.

This differs from crawling the public website.
Because we build and serve the site ourselves, we can use the repository's navigation metadata as the site map, include local source changes that are not deployed publicly, pin and reproduce the toolchain, and control the extraction and cleanup before conversion.
It also avoids depending on the public site's current deployment, redirects, analytics, robots rules, or unrelated page chrome.

Examples: `devbox` with Mintlify
