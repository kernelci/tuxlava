# -*- coding: utf-8 -*-

import copy
import json

import pytest

from tuxlava.tuxmake import InvalidTuxBuild, TuxBuildBuild, TuxMakeBuild

metadata = {
    "results": {
        "artifacts": {"kernel": ["bzImage"], "modules": ["modules.tar.xz"]},
    },
    "build": {"target_arch": "arm64"},
}


def build_directory(directory, metadata=metadata):
    directory.mkdir()
    (directory / "metadata.json").write_text(json.dumps(metadata))
    return directory


@pytest.fixture
def directory(tmp_path):
    return build_directory(tmp_path / "tuxmake-build")


@pytest.fixture
def directory_with_invalid_metadata(tmp_path):
    d = tmp_path / "invalid-metadata"
    d.mkdir()
    (d / "metadata.json").touch()
    return d


@pytest.fixture
def directory_with_empty_metadata(tmp_path):
    d = tmp_path / "invalid-metadata"
    d.mkdir()
    (d / "metadata.json").write_text("{}", encoding="utf-8")
    return d


@pytest.fixture
def tuxmake_build(directory):
    return TuxMakeBuild(directory)


class TestTuxMakeBuild:
    def test_kernel(self, tuxmake_build, directory):
        assert tuxmake_build.kernel == f"file://{directory / 'bzImage'}"

    def test_modules(self, tuxmake_build, directory):
        assert tuxmake_build.modules[0] == f"file://{directory / 'modules.tar.xz'}"

    def test_target_arch(self, tuxmake_build):
        assert tuxmake_build.target_arch == "arm64"

    def test_no_kernel(self, tmp_path):
        metadata1 = copy.deepcopy(metadata)
        del metadata1["results"]["artifacts"]["kernel"]
        directory = build_directory(tmp_path / "build", metadata1)
        with pytest.raises(TuxMakeBuild.Invalid):
            TuxMakeBuild(directory)

    def test_no_modules(self, tmp_path):
        metadata1 = copy.deepcopy(metadata)
        del metadata1["results"]["artifacts"]["modules"]
        directory = build_directory(tmp_path / "build", metadata1)
        tuxmake_build = TuxMakeBuild(directory)
        assert not tuxmake_build.modules

    def test_no_metadata(self, tmp_path):
        with pytest.raises(InvalidTuxBuild):
            TuxMakeBuild(tmp_path)

    def test_no_directory(self, tmp_path):
        f = tmp_path / "somefile"
        f.touch()
        with pytest.raises(InvalidTuxBuild):
            TuxMakeBuild(f)

    def test_invalid_metadata(self, directory_with_invalid_metadata):
        with pytest.raises(InvalidTuxBuild):
            TuxMakeBuild(directory_with_invalid_metadata)

    def test_empty_metadata(self, directory_with_empty_metadata):
        with pytest.raises(InvalidTuxBuild):
            TuxMakeBuild(directory_with_empty_metadata)


@pytest.fixture
def url(get, mocker):
    get.side_effect = [mocker.Mock(status_code=200, text=json.dumps(metadata))]
    return "https://example.com"


@pytest.fixture
def tuxbuild_build(url):
    return TuxBuildBuild(url)


class TestTuxBuildBuild:
    def test_kernel(self, tuxbuild_build):
        assert tuxbuild_build.kernel == "https://example.com/bzImage"

    def test_modules(self, tuxbuild_build):
        assert tuxbuild_build.modules[0] == "https://example.com/modules.tar.xz"

    def test_http_error(self, get, mocker, url):
        get.side_effect = [mocker.Mock(status_code=404)]
        with pytest.raises(InvalidTuxBuild):
            TuxBuildBuild(url)
