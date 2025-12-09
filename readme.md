<div align="center">
  <h1>🪝 Hook 🪝</h1>
  <i>Not the annoying social media ones..</i>
</div>

## 🔴 Description

A small Python `build-system` middleware for [hatchling](https://hatch.pypa.io/latest/) that:
- Dynamically resolves `@ git+` dependencies into `~={latest}` workspace or git version [^git]
- Pins all package versions to `==` when building a [Pyaket](https://pyaket.dev/) executable, for reproducibility.

[^git]: Wheels cannot have direct references on PyPI, so we update the metadata at build time in the order found in `(workspace > git)`. This also allows for decoupled installation of projects that depend on each other outside a [workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/), latest git only.

## 🟡 Usage

> [!IMPORTANT]
> I recommend making your own hook package based on this one instead of using it directly, as it may change over time and not fit your particular needs or use cases.

Have the following in your `pyproject.toml`:

```toml
[project]
dependencies = [
  # Resolves to ~={latest} on wheels
  "shared @ git+...",
  "engine @ git+...",
]

[build-system]
requires = ["hatchling", "hook@git+https://github.com/BrokenSource/Hook/"]
build-backend = "hatchling.build"

[tool.hatch.metadata.hooks.plugin]
# Intentionally empty

[tool.hatch.metadata]
allow-direct-references = true
```

> [!NOTE]
> Avoid using `requires = ["hook"]`, as it'll use the unrelated [`hook`](https://pypi.org/project/hook/) package (name collision)
> - You can publish a custom name package and use it instead of git references

A small optimization for iterative development or avoiding network calls is to set the `hook` package as a [workspace source](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-sources) if using [uv](https://docs.astral.sh/uv/), either in your main `pyproject.toml` or per-project:

```toml
[tool.uv.sources]
hook = {workspace=true}
```

## 🟢 Security

For transparency, this middleware purely solves a technical limitation of Python packaging for monorepos - installing and building packages outside a workspace, by rewriting project dependencies at build time.

It may seem like a convoluted solution, but it's a practical workaround until uv improves monorepo tooling.

What _can be_ frowned upon is using `hook@git+...` instead of publishing a package:

- This is done for simplicity in not having to manage, semver, name a tiny package.
- Building older versions of projects is only supported on a checked-out monorepo.

The [source code](./hook/__init__.py) is short and easy to audit.
