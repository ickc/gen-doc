This builds single file targets from documentations, primarily for the purpose of feeding into LLMs to chat with doc.

# Notes

Each subdirectories should contains a single documentation project. Within each, it must contains

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

### Simply Download

Examples: `pandoc`, `Pkg.jl`

### Simply concat

In some cases, the documentation framework used in a project does not have an option to produce single file documentation. We will then simply concat all relevant doc files and call it a day.

Examples: `devbox`, `flox`

### Crawl & concat

Some projects doesn't even provide the source of documentation. We will use this recipe instead:

1. crawl by wget
2. convert to markdown by pandoc
3. concat

Previous example: [`flox`](https://github.com/ickc/gen-doc/blob/416d3a941537cd767a63900b3dde5f72ba0f82c6/flox/makefile)

### Simply build

We will use the original build system to produce a single file target that is not provided.

Example: `python-patterns` with sphinx

### Tweak & rebuild

We would dive into the doc build framework and tweak it so that single file target are produced.

Examples:

- `nersc`, `pixi` with mkdocs and additional plugin `print-site`
