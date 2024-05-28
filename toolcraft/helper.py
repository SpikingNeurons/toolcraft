
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
from . import richy

_LOGGER = logger.get_logger()


@dataclasses.dataclass(frozen=True)
class TfInstallFromSource(s.DownloadFileGroup):
    """

    Referred from: https://www.tensorflow.org/install/source_windows

    [1] Install pip packages

    pip3 install six numpy wheel
    pip3 install keras_applications==1.0.6 --no-deps
    pip3 install keras_preprocessing==1.0.5 --no-deps

    [2] Install Bazel

    Copy to `C:/bazel`
    Rename to `bazel.exe`

    [3] Install cuda

    [4] Install cudnn

    Extract cudnn and copy to
     > C://Program Files//NVIDIA GPU Computing Toolkit//CUDA//vXX.X

    [5] Install msys2

    Install msys2 to `C:\msys64`

    Then in `cmd` do `pacman -S git patch unzip`

    [6] Checkout source code

    cd tensorflow
    git pull
    git checkout tags/v2.5.0
    git restore .

    [7] Configure

    python ./configure.py

    > Opt for compute capability 7.5 (both for RS laptop and workstation same

    [8] Bazel build on machine with internet (for GPU)

    ```
    bazel build --config=opt --config=cuda --define=no_tensorflow_py_deps=true //tensorflow/tools/pip_package:build_pip_package
    bazel-bin\tensorflow\tools\pip_package\build_pip_package C:/tmp/tensorflow_pkg
    ```

    [9] Install package (or copy to RS machine)

    cd C:\tmp\tensorflow_pkg
    pip3 uninstall -y tensorflow
    pip3 install tensorflow-2.5.0-cp39-cp39-win_amd64.whl
    """

    class LITERAL(s.DownloadFileGroup.LITERAL):
        bazel = "bazel-3.7.2-windows-x86_64.exe"
        cuda = "cuda_11.2.2_461.33_win10.exe"
        cudnn = "cudnn-11.2-windows-x64-v8.1.1.33.zip"
        msys2 = "msys2-x86_64-20210604.exe"

    @property
    def name(self) -> str:
        return "tensorflow_v2.5.0"

    @property
    def meta_info(self) -> dict:
        return {}

    @property
    @util.CacheResult
    def root_dir(self) -> pathlib.Path:
        return pathlib.Path.home() / "Downloads" / ".tensorflow"

    # noinspection SpellCheckingInspection
    def get_urls(self) -> t.Dict[str, str]:
        return {
            self.LITERAL.bazel: "https://github.com/bazelbuild/bazel/releases/"
                                "download/3.7.2/bazel-3.7.2-windows-x86_64.exe",
            self.LITERAL.cuda: "https://developer.download.nvidia.com/compute/"
                               "cuda/11.2.2/local_installers/"
                               "cuda_11.2.2_461.33_win10.exe",
            self.LITERAL.cudnn: "https://developer.download.nvidia.com/"
                                "compute/machine-learning/cudnn/secure/"
                                "8.1.1.33/11.2_20210301/"
                                "cudnn-11.2-windows-x64-v8.1.1.33.zip?"
                                "rO8QEu6qUd-7Odu9DHMQwILLnzOFmI21LxxnFk_CJx4oD"
                                "a66FWh7gUZ8XYlnM7RRAlvfao2HFT_pejwAoL2hS68rmb"
                                "pbl2j1soMJPOtUwr8AtWNkI3r_iMTrpsETC5Jiojkyrx"
                                "_G65xw00s3ian0tjR1XoyJdnfMlyjFQSIA3IXUDKz3kWP"
                                "RIoyKIxY376w_wHakpxcDNJCC9VVqDtNYtg",
            self.LITERAL.msys2: "https://repo.msys2.org/distrib/x86_64/"
                                "msys2-x86_64-20210604.exe"
        }

    # noinspection SpellCheckingInspection
    def get_hashes(self) -> t.Dict[str, str]:
        return {
            self.LITERAL.bazel: "ecb696b1b9c9da6728d92fbfe8410bafb4b3a65c35898"
                                "0e49742233f33f74d10",
            self.LITERAL.cuda: "e572654ac90ea720b73cf72f14af6b175dddf4ff282af8"
                               "22e32c19d63f0284c4",
            self.LITERAL.cudnn: "449dac158c423a2e682059650043cd6056a9d7cdfaedb"
                                "bd056029df1e7229889",
            self.LITERAL.msys2: "2e9bd59980aa0aa9248e5f0ad0ef26b0ac10adae7c6d3"
                                "1509762069bb388e600",
        }


@dataclasses.dataclass(frozen=True)
class PyCharmDownloader(s.DownloadFileGroup):

    version: str
    professional: bool

    @property
    def name(self) -> str:
        _p_or_c = 'professional' if self.professional else 'community'
        return f"pycharm-{_p_or_c}-{self.version}"

    @property
    def meta_info(self) -> dict:
        return {}

    @property
    @util.CacheResult
    def root_dir(self) -> pathlib.Path:
        return pathlib.Path.home() / "Downloads" / ".pycharm"

    def get_urls(self) -> t.Dict[str, str]:
        return {
            f"{self.name}.exe":
                f"https://download-cf.jetbrains.com/python/{self.name}.exe",
        }

    def get_hashes(self) -> t.Dict[str, str]:
        # noinspection SpellCheckingInspection
        return {
            f"{self.name}.exe": "1678f05cb177b57fa82bb7fd14f16e191c3aaf4caad13"
                                "5242319855df3908e66",
        }


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
    def _root_dir(self) -> pathlib.Path:
        return pathlib.Path.home() / "Downloads" / ".python"

    def get_urls(self) -> t.Dict[str, str]:
        return {
            f"{self.name}.exe":
                f"https://www.python.org/ftp/python/"
                f"{self.version}/{self.name}.exe",
        }

    def package_it(self) -> pathlib.Path:

        with richy.StatusPanel(
            title=f"Packaging {self.name}",
            tc_log=_LOGGER,
        ) as _rp:

            with self(richy_panel=_rp):

                # if not created, then create
                if not self.is_created:
                    self.create()

                # get paths and if exist return
                _exe_path = self.upath / f"{self.name}.exe"
                _zip_path = self.upath.parent / f"{self.name}.zip"
                if _zip_path.exists():
                    return _zip_path

                # get all related debug files
                _rp.text = f"getting debug symbols and all related files"
                os.system(
                    f"{_exe_path.resolve().as_posix()} /layout"
                )

                # zip all files
                _rp.text = f"zipping files"
                _zip = zipfile.ZipFile(_zip_path, mode="w")
                for _f in self.upath.iterdir():
                    _zip.write(_f, _f.name)
                    if _f != _exe_path:
                        _f.unlink()
                _zip.write(self.info.upath, self.info.upath.name)
                _zip.write(self.config.upath, self.config.upath.name)
                _zip.close()

                # deleting
                _rp.text = f"deleting files"

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



