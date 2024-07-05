This builds single file targets from documentations, primarily for the purpose of feeding into LLMs to chat with doc.

# Notes

Each subdirectories should contains a single documentation project. Within each, it must contains

- `makefile` with targets `single_file`, `all`, `clean`, `Clean`, s`update`.

    - `single_file` should make the best single file target, and make a copy at `build/` with the name of that subdirectory and an appropriate extension.

    - `all` make all single file targets, including `single_file` and optionally other alternative single file targets.

    - `clean` cleanup generated files.

    - `Clean` is a more thorough cleanup, including other things that are more expensive to generate such as the environment.

    - `update` will update the doc to point to the latest one, and also the environment if present.

- `.gitignore`

- optionally `README.md`

# Tips and examples

- For downloading from GitHub, see the `pandoc/` example.

- For adding a git submodule and building a single page target, see the `nersc/` example.

- For generic website crawling and concat, see the `flox/` example.

- For concatenation of multiple source files, see the `nersc/` and `devbox/` examples.
