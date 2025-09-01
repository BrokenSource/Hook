import os
import subprocess
import sys
from functools import cache
from subprocess import PIPE

from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.plugin import hookimpl


@cache
def get_version(package: str) -> str:
    package = package.split("[")[0]
    process = subprocess.run((
        sys.executable, "-m",
        "uv", "version",
        "--package", package,
        "--color", "never",
        "--short",
    ), stdout=PIPE)

    # Within the monorepo, pyproject version
    if process.returncode == 0:
        output = process.stdout.decode("utf-8")
        return output.strip()

    # Standalone mode
    return "0.0.0"


class BrokenHook(MetadataHookInterface):
    PLUGIN_NAME = "plugin"

    def update(self, metadata: dict) -> None:

        # Trick to replace all list items in place
        def patch(items: list[str]) -> None:
            for (x, item) in enumerate(items):
                item = item.replace(" ", "")

                # Replace git+ dependencies
                if (git := "@git+") in item:
                    package = item.split(git)[0]
                    version = get_version(package)
                    item    = f"{package}~={version}"

                # Pin versions on release binaries
                if (os.getenv("PYAKET_RELEASE", "0") == "1"):
                    for pin in ("~=", ">=", "<="):
                        item = item.replace(pin, "==")

                items[x] = item

        # Patch all normal and optional dependencies
        list(map(patch, metadata.get("optional-dependencies", {}).values()))
        patch(metadata.get("dependencies", {}))


@hookimpl
def hatch_register_metadata_hook():
    return BrokenHook
