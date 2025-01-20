#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import docker
import os
import sys
from pathlib import Path

BASE = (Path(__file__) / "..").resolve()


def main():
    client = docker.from_env(version="1.38")
    print("Checking for LAVA validity")
    directory_path = BASE / "unit" / "refs" / "definitions"
    print(directory_path)
    files = [file for file in os.listdir(directory_path) if file.endswith(".yaml")]
    for filename in files:
        print(f"{filename=}")
        container = client.containers.run(
            image="registry.gitlab.com/lava/lava/amd64/lava-dispatcher:2024.09.dev0167",
            command="/usr/share/lava-common/lava-schema.py job /data/%s" % filename,
            volumes={"%s" % directory_path: {"bind": "/data", "mode": "rw"}},
            detach=True,
        )
        container_exit_code = container.wait()
        logs = container.logs().decode("utf-8")
        if container_exit_code["StatusCode"] != 0:
            print(f"FAIL: Checking for LAVA validity, filename '{filename}'")
            print(f"Error details:\n{logs}")
            exit(1)


if __name__ == "__main__":
    sys.exit(main())
