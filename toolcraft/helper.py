
import dataclasses
import typing as t
import pathlib
import os
import zipfile
import sys
import shutil

from . import storage as s
from . import error as e
from . import util
from . import logger

_LOGGER = logger.get_logger()


@dataclasses.dataclass(frozen=True)
class PythonDownloader(s.DownloadFileGroup):
    version: str
    platform: str

    @property
    def name(self) -> str:
        return f"python-{self.version}-{self.platform}"

    @property
    def meta_info(self) -> dict:
        return {}

    @property
    def is_auto_hash(self) -> bool:
        return True

    @property
    @util.CacheResult
    def root_dir(self) -> pathlib.Path:
        return pathlib.Path.home() / "Downloads" / ".python"

    def get_urls(self) -> t.Dict[str, str]:
        return {
            f"{self.name}.exe":
                f"https://www.python.org/ftp/python/"
                f"{self.version}/{self.name}.exe",
        }

    def package_it(self) -> pathlib.Path:
        # get paths and if exist return
        _exe_path = self.path / f"{self.name}.exe"
        _zip_path = self.path.parent / f"{self.name}.zip"
        if _zip_path.exists():
            return _zip_path

        with logger.Spinner(
            title=f"Packaging {self.name}",
            logger=_LOGGER,
        ) as _s:

            # get all related debug files
            _s.text = f"getting debug symbols and all related files"
            os.system(
                f"{_exe_path.resolve().as_posix()} /layout"
            )

            # zip all files
            _s.text = f"zipping files"
            _zip = zipfile.ZipFile(_zip_path, mode="w")
            for _f in self.path.iterdir():
                _zip.write(_f, _f.name)
                if _f != _exe_path:
                    _f.unlink()
            _zip.write(self.info.path, self.info.path.name)
            _zip.write(self.config.path, self.config.path.name)
            _zip.close()

            # deleting
            _s.text = f"deleting files"

            # return
            return _zip_path


def pip_downloader(
    packages: t.List[t.Tuple[str, str]],
    python_installation_dir: str,
    store_for: str,
    force: bool = False,
    behind_firewall_settings: t.Dict[str, str] = None,
) -> pathlib.Path:
    # pip exe
    pip_exe = pathlib.Path(python_installation_dir) / "Scripts" / "pip.exe"
    python_exe = pathlib.Path(python_installation_dir) / "python.exe"
    pip_exe = pip_exe.resolve().as_posix()

    # create dir
    store_dir = pathlib.Path.home() / "Downloads" / ".pip_downloads" / store_for
    store_dir.mkdir(parents=True, exist_ok=True)
    zip_path = store_dir.parent / f"{store_for}.zip"

    # if zip exists return
    if force:
        if zip_path.exists():
            zip_path.unlink()
    if zip_path.exists():
        return zip_path
    for _f in store_dir.iterdir():
        _f.unlink()

    # first let us upgrade pip and setuptools
    os.system(
        f"{python_exe} -m pip install --upgrade pip"
    )
    os.system(
        f"{pip_exe} install setuptools -U"
    )

    # also download latest packages
    _pip_command = f"{pip_exe} download pip setuptools"
    _dest_command = f"--dest {store_dir.resolve().as_posix()}"
    os.system(
        f"{_pip_command} {_dest_command}"
    )

    # download source tar balls
    for package_name, package_version in packages:

        # all commands
        _pip_command = f"{pip_exe} download " \
                        f"{package_name}=={package_version}"
        _dest_command = f"--dest {store_dir.resolve().as_posix()}"

        # coalesce command
        _command = " ".join(
            [
                _pip_command,
                _dest_command,
            ]
        )

        # download
        os.system(
            _command
        )

    # derive all pip installs
    pip_installs = [
        'python -m pip install --upgrade pip',
        'pip install setuptools -U',
    ]
    _pip_install_line = "pip install"
    for package_name, package_version in packages:
        _pip_install_line += f" {package_name}=={package_version}"
    pip_installs.append(_pip_install_line)

    # create installation bats
    install_from_local_dir_script = \
        store_dir / 'install_from_local_dir.bat'
    install_from_local_dir_script.write_text(
        "\n".join(
            [f"{_} -f ." for _ in pip_installs]
        )
    )

    # if behind firewall setting are provided create bat script for it
    if behind_firewall_settings is not None:
        install_from_internal_repo_script = \
            store_dir / 'install_from_internal_repo.bat'
        index_url: str = behind_firewall_settings['index_url']
        trusted_host: str = behind_firewall_settings['trusted_host']
        install_from_internal_repo_script.write_text(
            "\n".join(
                [
                    f'pip config set global.index-url "{index_url}"',
                    f'pip config set global.trusted-host "{trusted_host}"',
                ] + pip_installs
            )
        )

    # copy python pip scripts
    python_pip_scripts_dir = pathlib.Path(__file__).parent / 'scripts'
    shutil.copy(
        python_pip_scripts_dir / 'pip_detect_redundant_packages.py',
        store_dir
    )
    shutil.copy(
        python_pip_scripts_dir / 'pip_package_mover.py',
        store_dir
    )

    # package in zip
    if zip_path.is_file():
        zip_path.unlink()
    _zip = zipfile.ZipFile(zip_path, mode="w")
    for _f in store_dir.iterdir():
        _zip.write(_f, _f.name)
    _zip.close()

    # return
    return zip_path



