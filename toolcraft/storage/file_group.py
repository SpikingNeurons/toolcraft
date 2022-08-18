"""
All we extend StorageHashable to save files

todo: add support for keepsake for saving blobs
  https://github.com/replicate/keepsake
  This library is very simple but may be we can do better storage or may be
  we add more fields to their existing proto buffers

todo: Lets figure out cloud hash mechanisms to confirm uploads or check downloaded files
  based on hashes in metadata of cloud file
  https://cloud.google.com/storage/docs/hashes-etags

todo: in context to mlflow this will also be used as log_artifact ... where
  we store arbitrary files
"""
import time

import requests
import typing as t
import subprocess
import dataclasses
import abc
import numpy as np
import gc
import datetime
import io
import hashlib
import zipfile
import gcsfs
import platform
import random
_now = datetime.datetime.now

from .. import util, logger, settings
from .. import storage as s
from .. import error as e
from .. import marshalling as m
from .. import richy
from . import StorageHashable
from .file_system import Path

# noinspection PyUnreachableCode
if False:
    from . import folder
    import tensorflow as tf

_LOGGER = logger.get_logger()

# noinspection PyUnresolvedReferences
USE_ALL = slice(None, None, None)

# note that this needs to be yaml serializable so do not have no.ndarray
# although it is supported by NpyMemMap
SELECT_TYPE = t.Union[
    int, slice, t.List[int],
]


@dataclasses.dataclass
class FileGroupConfig(s.Config):

    class LITERAL(s.Config.LITERAL):
        checked_on_list_limit = 5

    # updated when some sort of check is performed
    # + like hash check e.g. FileGroup, NpyGroup etc.
    # + schema checks e.g. Table
    checked_on: t.List[datetime.datetime] = dataclasses.field(
        default_factory=list
    )

    # note that after lot of thinking we decided to have auto hashes in
    # config as config is the place where it is apt to save it ... if we know
    # hashes or urls in advance we need not save that on disk as we can
    # extract it from instance ... But we always need to save auto-hashes as
    # we have no way to store them in the code ... also adding auto hashes to
    # *.info file i.e. hashable class is not recommended as hex_hash will
    # also depend on auto-hashes which is not clean ... so we now decide to
    # store it in config where we also have created_on timestamp ...
    # todo: the obvious problem here is when we move files to other machine
    #  the hex_hash is not representative of file hashes ... and hence we
    #  will need to look up config file ...
    #  ***
    #     and hence config will become important as deleting config also
    #     means you need to delete files generated
    #  ***
    #  The workaround is to have one more file like *.info or *.meta but that
    #  is out of scope and we need to have more better reason to have it ...
    #  as of now *.config will suffice.
    auto_hashes: dict = None

    @property
    @util.CacheResult
    def check_interval_choice(self) -> int:
        """
        Needed to cache as consecutive `periodic_check_needed` calls result
        in different results ... this ensures that for instance the
        randomness is consistent ...
        """
        return random.choice(settings.FileHash.CHECK_INTERVALS_IN_SEC)

    @property
    def periodic_check_needed(self) -> bool:
        # estimate if check needed
        if len(self.checked_on) == 0:
            return True
        else:
            _last_check_time = self.checked_on[-1]
            _delta_time = _now() - _last_check_time
            return int(_delta_time.total_seconds()) > \
                self.check_interval_choice

    # noinspection DuplicatedCode
    def append_checked_on(self):
        # this can never happen
        if len(self.checked_on) > self.LITERAL.checked_on_list_limit:
            raise e.code.CodingError(
                msgs=[
                    f"This should never happens ... did you try to append "
                    f"checked_on list multiple times"
                ]
            )
        # limit the list
        if len(self.checked_on) == self.LITERAL.checked_on_list_limit:
            self.checked_on = self.checked_on[1:]
        # append time
        self.checked_on.append(_now())


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['file_keys'],
)
class FileGroup(StorageHashable, abc.ABC):
    """
    todo: While file_group.py is for blob storage. In future we can enable it to
      use file_system.py (with no need for write, append filters like
      database features). This will nicely handle blob storage requirements as
      well as columnar storage for analytics. While data can move across
      multiple file systems. Model it based on table.py
      ...
      This might feel less priority as the main job of file_group will be to
      move data on internal servers rather than moving data on cloud for
      analytics. But we can think of scenarios where we might push big files
      on cloud storage.

    todo: also look for pyarrow.NativeFile that can be used by IPC routines
      and things like seek read can be done
    >>> import pyarrow as pa
    >>> pa.NativeFile

    What is file group?
    + A final leaf of our filing system
    + it can be
      + a single file with extension fg (you can override this)
      + multiple files starting with same self.name
      + a folder with extension fg (you can override this)
      + a mix of files and folders starting with self.name

    Note: All the parts in class that subclasses FileGroup if possible should
    have same data-structure. If the data-structure is different better have
    different FileGroup sub-class.

    Note that in manager module we have DynamicFileGroupsManager and
    StaticFileGroupsManager which can have subclass of FileGroup as fields.
    This makes it possible to access FileGroup's with different data-structures.

    *** VERY IMPORTANT NOTE ***
    + When using auto hash a yaml representation is serialized with computed
      hashes
    + Let say in future you modify create method which generates different
      data then there is no way the create method will be called until and
      unless you delete the previously generated files
    + So simple workaround is to check is_auto_hash property of FileGroup
      and delete the files on disk or manually delete all files so that
      create logic is called
    + Do not try to address this issue as the same thing applies for other
      FileGroup's where hash is provided

    """

    class LITERAL(StorageHashable.LITERAL):
        # used when keys are not defined for file_group ... especially useful
        # when there is only one file in the file group
        file = 'file'

    @property
    @util.CacheResult
    def config(self) -> FileGroupConfig:
        return FileGroupConfig(
            hashable=self,
        )

    @property
    @util.CacheResult
    def file_keys(self) -> t.List[str]:
        """
        Note that we need to know exactly what files sill be created even in
        case is_auto_hash. Do not expect code to handle dynamic file creation
        at runtime. Auto hashing is used when we do not know hash of file
        created but we still need to know the files that will be created.
        """
        return [self.LITERAL.file]

    @property
    def is_created(self) -> bool:
        """
        This does mean we need call to create_all

        todo: maybe not that big of a overhead but try to check if call to
          this property is minimal
        """
        # ----------------------------------------------------------------01
        # Note that if some file_groups are missing we raise error ... either
        # all file_groups should be present or none of them should exist
        _present_files = [
            (self.path / fk).exists() for fk in self.file_keys
        ]
        _all_files_in_fg_present = all(_present_files)
        _some_files_in_fg_present = any(_present_files)

        # ----------------------------------------------------------------02
        # check if state manager files available (The super method is
        # responsible to do this as state manager availability is checked there)
        _state_manager_files_available = super().is_created

        # ----------------------------------------------------------------03
        # if _state_manager_files_available then _all_file_groups_present=True
        if _state_manager_files_available:
            if not _all_files_in_fg_present:
                if _some_files_in_fg_present:
                    _msg = "But some files in the file group are missing"
                else:
                    _msg = "But all files in the file group are missing"

                raise e.code.CodingError(
                    msgs=[
                        f"State manager files for file group `{self.name}` "
                        f"are present in dir {self.path}.",
                        _msg,
                    ]
                )

        # ----------------------------------------------------------------04
        # if state manager files are not present then return False else if
        # all files present return True
        if _state_manager_files_available:
            return _all_files_in_fg_present
        else:
            return False

    @property
    def unknown_paths_on_disk(self) -> t.List[Path]:

        # container for unknown files
        _unknown_paths = []

        # look inside path dir if it exists
        if self.path.exists():
            # expect path to be a dir
            if self.path.isfile():
                raise e.code.CodingError(
                    msgs=[
                        f"We expect path to be a dir for FileGroup"
                    ]
                )
            # look inside path dir
            for _path in self.path.find(maxdepth=0, detail=False, withdirs=True):
                if _path.name in self.file_keys and _path.isfile():
                    continue
                # anything starting with `_` will be ignored
                # helpful in case you want to store results cached by `@s.dec.XYZ`
                # which uses `stores` property
                if _path.name.startswith("_"):
                    continue
                _unknown_paths.append(_path)

        # return
        return _unknown_paths

    @property
    def is_auto_hash(self) -> bool:
        return False

    @property
    def periodic_check_needed(self) -> bool:

        # if file creation needed do not call this method
        # todo: remove later
        if not self.is_created:
            raise e.code.CodingError(
                msgs=[
                    f"We need to create files before trying to do periodic "
                    f"check",
                    f"Please make a call to {self.__class__.__name__}.create",
                    f"Also make sure that you perform periodic check only "
                    f"after checking `file_creation_needed` is not True"
                ]
            )

        # return
        return self.config.periodic_check_needed

    @property
    def is_outdated(self) -> bool:
        return False

    # def __getattribute__(self, item: str) -> t.Any:
    #     """
    #     Helper method to access the files in group as annotated attributes.
    #     """
    #     # todo: if there is t.ClassVar annotation use their name to
    #     #  resolve the file and get() it here ... so that we can get files in
    #     #  FileGroup without file_key
    #     # a way to detect if field is class var
    #     # dataclasses._is_classvar('aa', typing)
    #     ...

    def explore(self):
        # for open with select
        # subprocess.Popen(r'explorer /select,"sadasdfas"')
        subprocess.Popen(f'explorer {self.path}')

    # noinspection PyMethodMayBeStatic
    def get_gcp_file_system(self) -> gcsfs.GCSFileSystem:
        """
        Refer:
        https://cloud.google.com/sdk/gcloud/reference/auth/application-default/login
        https://cloud.google.com/docs/authentication/getting-started#auth-cloud-implicit-python
        https://stackoverflow.com/questions/37003862/how-to-upload-a-file-to-google-cloud-storage-on-python-3
        """
        if platform.system() != "Windows":
            raise e.code.CodingError(
                msgs=[
                    "Only supported for windows platform"
                ]
            )

        # todo: update path for linux/unix
        _cred_file = Path.HOME / "AppData" / "Roaming" / "gcloud" / \
            "application_default_credentials.json"

        if not _cred_file.exists():
            raise e.code.NotAllowed(
                msgs=[
                    "Please make sure that gcloud is installed ...",
                    "Then run command `gcloud auth application-default login`",
                    f"This should ideally generate credential file {_cred_file} ...",
                    "Refer: https://cloud.google.com/sdk/gcloud/reference/auth/application-default/login"
                ]
            )

        _fs = gcsfs.GCSFileSystem(token=_cred_file.as_posix())

        return _fs

    def upload_to_gcp(self, bucket_name: str, folder_name: str, file_name: str):
        """
        Refer:
        https://filesystem-spec.readthedocs.io/en/latest/features.html

        Explore metadata option in `_fs.open()` for storing `self.info` and `self.config` states
        https://github.com/fsspec/gcsfs/issues/119
        """
        # get some vars
        _rp = self.richy_panel
        _fs = self.get_gcp_file_system()
        _file_to_make = f"{bucket_name}/{folder_name}/{file_name}"

        # check if already exists
        if _fs.exists(_file_to_make):
            e.code.NotAllowed(
                msgs=[
                    f"The file `{_file_to_make}` already exists on GCS ",
                    f"Use different name/location ..."
                ]
            )
            return

        # this can get buckets but does not work for now
        # todo: explore later
        # _fs.buckets

        # Zip in memory
        _rp.update(f"Make in memory zip file for {file_name}")
        _zip_buffer = io.BytesIO()
        with zipfile.ZipFile(
            file=_zip_buffer, mode='a', compression=zipfile.ZIP_DEFLATED
        ) as _zf:
            for _f in _rp.track(
                sequence=[
                    self.info.path, self.config.path
                ] + [self.path / _fk for _fk in self.file_keys],
                task_name="Zipping files",
            ):
                # noinspection PyTypeChecker
                _zf.write(_f, arcname=_f.name)
            _zf.close()

        # write to cloud
        # todo: make progressbar for streamed write
        # with _fs.transaction:  # todo: some issues with transaction
        _rp.update(f"Uploading `{file_name}` to cloud")
        with _fs.open(_file_to_make, 'wb') as _zf_on_gc:
            _zf_on_gc.write(_zip_buffer.getvalue())

    def get_hashes(self) -> t.Dict[str, str]:
        """
        If get_hashes is not overridden in child class we assume that
        Returns:

        """
        # in auto hash return hashes from config file
        if self.is_auto_hash:
            # we assume that the files will be created by now so we expect
            # the state_manager files to be present on the disk
            if not self.is_created:
                raise e.code.CodingError(
                    msgs=[
                        f"Never call this until files are created. Only after "
                        f"that the state files will be present on the disk"
                    ]
                )

            # check if auto_hashes present
            if self.config.auto_hashes is None:
                raise e.code.CodingError(
                    msgs=[
                        f"We expect that auto_hashes will be set by now"
                    ]
                )

            # return
            return self.config.auto_hashes

        # if not auto hash then raise error to inform to override this method
        else:
            raise e.code.NotAllowed(
                msgs=[
                    f"Since you have not configured for auto hashing we "
                    f"expect you to override this method to provide hashes "
                    f"dict.",
                    f"Please check:",
                    {
                        'class': self.__class__,
                        'name': self.name
                    }
                ]
            )

    @classmethod
    def hook_up_methods(cls):
        # call super
        super().hook_up_methods()

        # hook up get
        util.HookUp(
            cls=cls,
            method=cls.check,
            pre_method=cls.check_pre_runner,
            post_method=cls.check_post_runner,
        )

        # hook up get
        util.HookUp(
            cls=cls,
            method=cls.get_files,
            pre_method=cls.get_files_pre_runner,
            post_method=cls.get_files_post_runner,
        )

    def init_validate(self):
        # ---------------------------------------------------------- 01
        # call super
        super().init_validate()

        # ---------------------------------------------------------- 02
        # when is_auto_hash do not override get_hashes else override get_hashes
        if self.is_auto_hash:
            if FileGroup.get_hashes != self.__class__.get_hashes:
                raise e.code.CodingError(
                    msgs=[
                        f"When in auto hashing mode do not override get_hashes",
                        f"Please check:",
                        {
                            'class': self.__class__,
                            'name': self.name
                        }
                    ]
                )
        else:
            if FileGroup.get_hashes == self.__class__.get_hashes:
                raise e.code.CodingError(
                    msgs=[
                        f"When not in auto hashing mode please override "
                        f"get_hashes to provide hashes",
                        f"Please check:",
                        {
                            'class': self.__class__,
                            'name': self.name
                        }
                    ]
                )

        # ---------------------------------------------------------- 03
        # Check if hash strings are of proper length and lower case
        # we only do it when is_auto_hash!=True as then the
        # hashes will be provided in code .... note that otherwise the auto
        # hashes will anyways be compatible so no need to check them
        if not self.is_auto_hash:

            # get hashes and hashes_keys
            _hashes = self.get_hashes()
            _hashes_keys = _hashes.keys()

            # check hashes provided in hashes dict
            for k, _hash in _hashes.items():
                # check if key is known
                e.validation.ShouldBeOneOf(
                    value=k, values=self.file_keys,
                    msgs=[
                        f"The key {k} in hashes dict is not known"
                    ]
                ).raise_if_failed()
                # This is in case we want to let code print hash that we want
                # to supply
                # value should be a valid hash
                # if not len(_hash) == 64:
                #     raise e.code.NotAllowed(
                #         msgs=[
                #             f"Unsupported file hash for key {k!r}",
                #             f"We only support sha-256",
                #             f"Found hash {_hash!r} with length "
                #             f"{len(_hash)!r}"
                #         ]
                #     )
                # check if value is lower case
                if _hash.lower() != _hash:
                    raise e.code.NotAllowed(
                        msgs=[
                            f"For consistency make sure that hashes are "
                            f"lower case",
                            f"Found a hash {_hash!r} with upper case "
                            f"letter for key {k!r}."
                        ]
                    )

            # For file group it is mandatory to know all file hashes when it is
            # not auto hash so check if all hashes provided
            for k in self.file_keys:
                if k not in _hashes_keys:
                    raise e.code.CodingError(
                        msgs=[
                            f"Please provide hash for file_key `{k}` in "
                            f"`get_hashes` method of class {self.__class__}"
                        ]
                    )

        # ---------------------------------------------------------- 04
        # check if duplicate file_keys
        if len(self.file_keys) != len(set(self.file_keys)):
            raise e.validation.NotAllowed(
                msgs=[
                    f"We found some duplicates in self.file_keys",
                    self.file_keys
                ]
            )

    def on_enter(self):
        # call super
        super().on_enter()

        # NOTE: we only do this for file group and not for folders
        # if config.DEBUG_HASHABLE_STATE we will create files two times
        # to confirm if states are consistent and hence it will help us to
        # debug DEBUG_HASHABLE_STATE
        if settings.FileHash.DEBUG_HASHABLE_STATE:
            _info_backup_path = self.info.backup_path
            _config_backup_path = self.config.backup_path
            _info_backup_exists = _info_backup_path.exists()
            _config_backup_exists = _config_backup_path.exists()
            if _info_backup_exists ^ _config_backup_exists:
                raise e.code.CodingError(
                    msgs=[
                        f"We expect both info and config backup file to be "
                        f"present"
                    ]
                )
            if not _info_backup_exists:
                # create backup
                self.info.backup()
                self.config.backup()
                # delete things that were created in 03
                self.delete()
                # now let's create again
                self.create()
                # test info backup
                self.info.check_if_backup_matches()
                # test config backup
                self.config.check_if_backup_matches()

        # if created and outdated then delete and create them
        # if created and periodic check needed then perform periodic check
        # if files are not created create them
        # Note that this will make sure that if auto hashing the hashes are
        # generated
        if self.is_created:
            if self.is_outdated:
                # todo: dont try to `force=True` as it does not work ...
                #   It currently asks permission but that does not work ...
                #   hence just try to delete physically
                self.delete()
                self.create()
                self.check()
            if self.periodic_check_needed:
                self.check()
        else:
            self.create()
            self.check()

    def check_pre_runner(self, *, force: bool):
        # ~~~~~~~~~~~~ special check ~~~~~~~~~ to avoid coding bugs
        # Although redundant it helps avoid unnecessary calls to check ...
        # Example in case of FileGroup we can avoid long time consuming checks.
        # The check() must be called only needed to catch some coding errors we
        # do this
        if not self.is_created:
            raise e.code.CodingError(
                msgs=[
                    f"Do not try to check until all files are created, "
                    f"make sure to call {self.__class__.__name__}.create()",
                    f"Also make sure that you are first checking property "
                    f"`file_creation_needed` before calling check()"
                ]
            )
        # do not check for period if force check
        if not force:
            if not self.periodic_check_needed:
                raise e.code.CodingError(
                    msgs=[
                        f"Find the bug in the code, you need to make sure if "
                        f"periodic check is needed using property "
                        f"self.periodic_check_needed then only call this "
                        f"function"
                    ]
                )

    def do_hash_check(self, compute: bool) -> t.Dict:
        """
        When compute returns computed hashes else returns failed hashes if any ...

        If compute is false that means that in case of auto hash the hashes will
        already be computed and be present in config file
        """

        # ------------------------------------------------------ 01
        # some vars
        _rp = self.richy_panel
        _chunk_size = 1024 * 50
        _correct_hashes = {} if compute else self.get_hashes()
        _failed_hashes = {}
        _computed_hashes = {}
        _file_paths = {
            fk: self.path/fk for fk in self.file_keys
        }  # type: t.Dict[str, Path]
        _lengths = {}
        # get panels ... reusing richy.Progress.for_download as the stats
        # needed are similar
        if compute:
            _title = f"Compute Hash"
            _rp_key = "hash_compute_progress"
            _rp.update("computing hash ...")
        else:
            _title = f"Check Hash"
            _rp_key = "hash_check_progress"
            _rp.update("checking hash ...")
        _progress = richy.Progress.for_download_and_hashcheck(
            title=_title, tc_log=_LOGGER,
            box_type=richy.r_box.HORIZONTALS,
            border_style=richy.r_style.Style(color="cyan"),
            console=_rp.console)
        _rp[_rp_key] = _progress

        # ------------------------------------------------------ 02
        # now add tasks
        for fk in self.file_keys:
            _lengths[fk] = _file_paths[fk].stat()['size']
            _progress.add_task(
                task_name=fk, total=_lengths[fk]
            )

        # ------------------------------------------------------ 03
        # now check/compute hash
        for fk in self.file_keys:
            _hash_module = hashlib.sha256()
            # get task id
            with _file_paths[fk].open(mode='rb') as fb:
                # compute
                for _chunk in iter(lambda: fb.read(_chunk_size), b''):
                    _hash_module.update(_chunk)
                    _progress.tasks[fk].update(advance=len(_chunk),)
                fb.close()
                _computed_hash = _hash_module.hexdigest()
            # make dicts to return
            _computed_hashes[fk] = _computed_hash
            if not compute:
                if _computed_hash != _correct_hashes[fk]:
                    _progress.tasks[fk].failed()
                    _failed_hashes[fk] = {
                        'correct  ': _correct_hashes[fk],
                        'computed ': _computed_hash,
                    }

        # ------------------------------------------------------ 04
        # now remove progress indicator to save some spaces in render panel
        del _rp[_rp_key]

        # ------------------------------------------------------ 05
        # return
        if compute:
            return _computed_hashes
        else:
            return _failed_hashes

    # noinspection PyUnusedLocal
    def check(self, *, force: bool = False):
        """

        todo: we can make this with asyncio with aiohttps and aiofiles
          https://gist.github.com/darwing1210/c9ff8e3af8ba832e38e6e6e347d9047a

        """
        # get failed hashes
        _failed_hashes = self.do_hash_check(compute=False)

        # delete state files and print failed hashes
        if bool(_failed_hashes):
            # wipe state manager files
            self.info.delete()
            self.config.delete()
            # raise error
            raise e.code.CodingError(
                msgs=[
                    f"Hashes for some files did not match. ",
                    f"FileGroup: {self.name}",
                    f"Check below",
                    _failed_hashes,
                    f"Check file system {self.path}"
                ]
            )

    # noinspection PyUnusedLocal
    def check_post_runner(
        self, *, hooked_method_return_value: t.Any, force: bool
    ):

        # since things are now checked write to disk but before that make
        # sure to add checked on info
        self.config.append_checked_on()

    def get_files_pre_runner(
        self, *,
        file_keys: t.List[str]
    ):
        """

        todo:
          In case where multiple python objects are using same FileGroup we
          will lust add who accessed in last_accessed_on list in Config. Note
          that this may be possible as we every time load file make it
          editable and then save and make it read lock ... we can ensure some
          sort of critical locking mechanism so that multiple
          threads/instances can use the FileGroup files

        todo: lock the config file so that no one else can access it
        """
        # --------------------------------------------------------------01
        # validations
        for file_key in file_keys:
            # ----------------------------------------------------------01.01
            # check if in file keys
            if file_key not in self.file_keys:
                raise e.code.CodingError(
                    msgs=[
                        f"The supplied `file_key={file_key}` to "
                        f"`{self.__class__}.get_file` method is not one of:",
                        self.file_keys
                    ]
                )

        # --------------------------------------------------------------02
        # check if created
        if not self.is_created:
            raise e.validation.NotAllowed(
                msgs=[
                    f"Make sure to create files for instance of type "
                    f"{self.__class__} before calling `get_files()`"
                ]
            )

        # --------------------------------------------------------------03
        # if periodic check needed
        if self.periodic_check_needed:
            raise e.validation.NotAllowed(
                msgs=[
                    f"Make sure to perform check before using `get_files()` "
                    f"for class {self.__class__}"
                ]
            )

        # --------------------------------------------------------------04
        # delete if outdated
        if self.is_outdated:
            raise e.validation.NotAllowed(
                msgs=[
                    f"Files are out dated for class {self.__class__}. You "
                    f"need to delete it."
                ]
            )

    def get_files(
        self, *, file_keys: t.List[str]
    ) -> t.Dict[str, Path]:
        """
        Default is to return Path
        """
        return {
            file_key: self.path / file_key
            for file_key in file_keys
        }

    # noinspection PyUnusedLocal
    def get_files_post_runner(
            self, *, hooked_method_return_value: t.Dict[str, t.Any], file_keys: t.List[str]
    ):
        # --------------------------------------------------------------01
        # we are getting data so update the access info
        self.config.append_last_accessed_on()

    def get_file(self, file_key: str) -> s.Path:
        return self.get_files(file_keys=[file_key])[file_key]

    # noinspection PyUnusedLocal
    def create_pre_runner(self):
        """
        User has to take care to keep files on disk ... or provide mechanism
        to create all the files by overriding create() method
        """
        # --------------------------------------------------------------01
        # call super ... checks if created
        super().create_pre_runner()

        # --------------------------------------------------------------02
        # create path dir if it does not exist
        # Note that FileGroup is a folder with file names file_keys inside it
        if not self.path.exists():
            self.path.mkdir()

        # --------------------------------------------------------------03
        # if unknown files present throw error
        _unknown_files = self.unknown_paths_on_disk
        if bool(_unknown_files):
            raise e.code.NotAllowed(
                msgs=[
                    f"We were trying to create files for class "
                    f"{self.__class__.__name__!r} with base name "
                    f"{self.name!r} in dir `{self.path}` but, we "
                    f"found below unknown files",
                    [f.name for f in _unknown_files]
                ]
            )

    def create(self) -> t.List[Path]:
        # some vars
        _rp = self.richy_panel
        _iterable = self.file_keys
        _total_files = len(_iterable)
        _rp.update(f"creating {_total_files} files")
        _iterable = _rp.track(
            self.file_keys, task_name=f"create {_total_files} files #")

        # create
        _ret = []
        for k in _iterable:

            # get expected file from key
            _expected_file = self.path / k

            # if found on disk bypass creation for efficiency
            if _expected_file.isfile():
                _ret.append(_expected_file)
                continue

            # if expected file not present then create
            _created_file = _expected_file if _expected_file.exists() else \
                self.create_file(file_key=k)

            # if check if created and expected file is same
            if _expected_file != _created_file:
                if not isinstance(_created_file, Path):
                    raise e.code.CodingError(
                        msgs=[
                            f"You are supported to return instance of {Path} ... "
                            f"instead found {type(_created_file)}"
                        ]
                    )
                raise e.code.CodingError(
                    msgs=[
                        f"The {self.__class__}.create() returns file path "
                        f"which is not expected for key {k!r}",
                        {
                            "Expected": _expected_file,
                            "Found": _created_file,
                        },
                    ]
                )

            # append
            _ret.append(_expected_file)

        # return list of created files
        return _ret

    def create_post_runner(
        self, *, hooked_method_return_value: t.List[Path]
    ):
        """
        The files are now created let us now do post handling
        # todo: if failed delete files that are created
        """
        created_fs = hooked_method_return_value
        expected_fs = [self.path / fk for fk in self.file_keys]

        # ----------------------------------------------------------------01
        # validation
        # ----------------------------------------------------------------01.01
        # created files should be `list` and should not be empty
        if not isinstance(created_fs, list):
            raise e.code.CodingError(
                msgs=[
                    f"Expected a list from {self.__class__.create_file} but "
                    f"instead found returned value of type "
                    f"{type(created_fs)}"
                ]
            )
        # ----------------------------------------------------------------01.02
        # check if created file is proper and if it is on disk
        for f in created_fs:
            if not isinstance(f, Path):
                raise e.code.CodingError(
                    msgs=[
                        f"Method {self.create_file} should return the list of "
                        f"files created, instead found {created_fs}"
                    ]
                )
            if f not in expected_fs:
                raise e.code.CodingError(
                    msgs=[
                        f"File {f.name!r} generated by create method of class "
                        f"{self.__class__} does not correspond to one of the "
                        f"file keys given by property self.file_keys",
                        self.file_keys
                    ]
                )
            if not f.exists():
                raise e.code.CodingError(
                    msgs=[
                        f"One of the file {f} you are returning from "
                        f"self.create_file() is not present on the disk"
                    ]
                )
        # ----------------------------------------------------------------01.03
        # check if all key_paths i.e expected files are generated
        for f in expected_fs:
            if f not in created_fs:
                raise e.code.CodingError(
                    msgs=[
                        f"We expect file {f.name} to be created",
                        f"But the file was not created"
                    ]
                )

        # ----------------------------------------------------------------02
        # if unknown files present throw error
        _unknown_files = self.unknown_paths_on_disk
        if bool(_unknown_files):
            raise e.code.NotAllowed(
                msgs=[
                    f"We have created files for class "
                    f"{self.__class__.__name__!r} with base name "
                    f"{self.name!r} in dir {self.path}. Below "
                    f"unknown files were also created along with it.",
                    [f.name for f in _unknown_files]
                ]
            )

        # ----------------------------------------------------------------03
        # make files read only
        # todo: not sure how to make our `Path` based on fsspec as readonly
        # for f in created_fs:
        #     util.io_make_path_read_only(f)

        # ----------------------------------------------------------------04
        # call super and return .... so that state is created
        _ret = super().create_post_runner(
            hooked_method_return_value=hooked_method_return_value)

        # ----------------------------------------------------------------05
        # in case of auto hashing we need to generate hashes and save it in
        # config ....
        # Note we call super above as below code will generate config file on
        # disc and hence super will raise error ... in super the auto_hashes
        # will get set to None and then here we update it after computing hashes
        if self.is_auto_hash:
            if self.config.auto_hashes is not None:
                raise e.code.CodingError(
                    msgs=[
                        f"We just generated files so we do not expect auto "
                        f"hashes to be present in the config"
                    ]
                )
            _auto_hashes = self.do_hash_check(compute=True)
            self.config.auto_hashes = _auto_hashes

        # ----------------------------------------------------------------06
        # return
        return _ret

    @abc.abstractmethod
    def create_file(self, *, file_key: str) -> Path:
        """
        If for efficiency you want to create multiple files ... hack it to
        create files on first call and subsequent file_keys will just fake
        things to return path.

        Note: create can only return file path and nothing else
        """
        ...

    def delete(self, *, force: bool = False) -> t.Any:
        """
        Deletes FileGroup

        Note: Do not do read_only check here as done in delete_item method as
        it is not applicable here and completely depends on parent folder
        permissions
        """
        # todo: this gets called from within spinner that is added while this
        #  method was hooked with delete_pre_runner and delete_post_runner
        #  ... so we want to pause spinner so that user response can be
        #  grabbed to delete files

        # ---------------------------------------------------------------01
        _rp = self.richy_panel
        if settings.FileHash.DEBUG_HASHABLE_STATE:
            # if config.DEBUG_HASHABLE_STATE we know what we are doing ... we
            # are debugging and there will be one time programmatically delete
            # so set the response automatically for FileGroup
            force = True
            _rp.update(
                "Deleting files automatically for file group [DEBUG_HASHABLE_STATE is True]"
            )

        # ---------------------------------------------------------------02
        # delete
        # We ask for user response as most of the files/folders are important
        # and programmatically deletes will cost download or generation of
        # files ...
        # This can be easily bypasses by setting force == True
        if force:
            response = "y"
        else:
            # todo: need to implement the ask dialog inside richy_panel
            raise e.code.NotYetImplemented(msgs=["todo: need to implement the ask dialog inside richy_panel"])
            # response = richy.r_prompt.Confirm.ask(
            #     f"Do you want to delete files for FileGroup `{self.path}`?",
            #     default=True,
            # )

        # ---------------------------------------------------------------03
        # perform action
        if response == "y":

            # -----------------------------------------------------------03.01
            # some variables to indicate progress
            # todo: make it like progress bar
            _total_keys = len(self.file_keys)
            _s_fmt = len(str(_total_keys))

            # -----------------------------------------------------------03.02
            # delete all files for the group
            _rp.update("deleting files ...")
            for fk in self.file_keys:
                _key_path = self.path / fk
                if _key_path.exists():
                    _key_path.rm_file()
                else:
                    raise e.code.CodingError(
                        msgs=[
                            f"If you deleted files manually this can happen",
                            f"But if you didnt then this might be a bug",
                            f"We were not able to find file {fk} for file_group "
                            f"with path {self.path}"
                        ]
                    )
        else:
            raise e.code.ExitGracefully(
                msgs=[
                    "We will terminate the program as you requested "
                    "not to delete files..."
                ]
            )


@dataclasses.dataclass(frozen=True)
class NpyFileGroup(FileGroup, abc.ABC):
    """
    Rationale: In all subclasses do not cache the properties that return
      memory map to numpy arrays ... this will keep references alive and hence
      python garbage collection will not take over
    """

    @property
    @abc.abstractmethod
    def shape(self) -> t.Dict[str, t.Tuple]:
        ...

    @property
    @abc.abstractmethod
    def dtype(self) -> t.Dict[str, t.Any]:
        ...

    @property
    @util.CacheResult
    def lengths(self) -> t.Dict[str, int]:
        return {
            k: len(util.npy_load(p, memmap=True)) for k, p in self.get_files(file_keys=self.file_keys).items()
        }

    @property
    def has_arbitrary_lengths(self) -> bool:
        _len = None
        for _l in self.lengths.values():
            if _l == 1:
                continue
            if _len is None:
                _len = _l
                continue
            if _len != _l:
                return True
            else:
                continue
        return False

    def get_tf_dataset(
        self, batch_size: int, num_batches: int, memmap: bool,
        expected_element_spec: t.Dict[str, "tf.TensorSpec"]
    ) -> "tf.data.Dataset":
        try:
            # import
            import tensorflow as tf

            # get data
            _data = self.load_as_dict(fix_all_lengths_same=True, memmap=memmap)

            # skip some elements that are not needed
            _elements_to_skip = [_ for _ in _data.keys() if _ not in expected_element_spec.keys()]
            for _ in _elements_to_skip:
                del _data[_]

            # make dataset
            _ds = tf.data.Dataset.from_tensor_slices(_data).batch(batch_size).take(num_batches)

            # validate element spec
            e.validation.ShouldBeEqual(
                value1=expected_element_spec, value2=_ds.element_spec,
                msgs=["Was expecting the element spec to be identical"]
            ).raise_if_failed()

            # return
            return _ds
        except ImportError as _e:
            raise e.code.CodingError(
                msgs=["Cannot create tensorflow dataset as tensorflow is not available ..."]
            )

    def load_as_dict(
        self, memory_limit_in_gbytes: int = None, fix_all_lengths_same: bool = False, memmap: bool = True
    ) -> t.Dict[str, t.Union[np.ndarray, t.Dict[str, np.ndarray]]]:
        """
        Full load in memory for fast access
        """
        self.richy_panel.update("loading NpyFileGroup as dict")
        # -------------------------------------------------- 01
        # validate
        # todo: test memory limit
        if memory_limit_in_gbytes is not None:
            raise e.code.NotYetImplemented(
                msgs=["This feature is not yet implemented"]
            )
        if fix_all_lengths_same:
            if self.has_arbitrary_lengths:
                raise e.code.NotAllowed(
                    msgs=[f"This {self.__class__} has files with arbitrary lengths "
                          f"so we cannot make all lengths fixed "]
                )

        # -------------------------------------------------- 02
        # get all in memory ... note we load via get_files so access info is saved to config files ...
        _ret = {
            _k: self.load_npy_data(file_key=_k, memmap=memmap)
            for _k, _ in self.get_files(file_keys=self.file_keys).items()
        }

        # -------------------------------------------------- 03
        # augment singular elements
        if fix_all_lengths_same:
            _len = None
            for _k in self.file_keys:
                if len(_ret[_k]) != 1:
                    _len = len(_ret[_k])
                    break
            if _len is None:
                raise e.code.ShouldNeverHappen(msgs=[])
            for _k in self.file_keys:
                if len(_ret[_k]) == 1:
                    _ret[_k] = np.repeat(_ret[_k][:], _len, axis=0)

        # -------------------------------------------------- 04
        # return
        return _ret

    def load_npy_data(self, file_key: str, memmap: bool) -> t.Union[np.ndarray, t.Dict[str, np.ndarray]]:
        """
        Note that for npy record the type is t.Dict[str, np.ndarray]
        As we can treat it as dict of numpy arrays
        """
        return util.npy_load(self.path / file_key, memmap=memmap)

    def save_npy_data(
        self,
        file_key: str,
        npy_data: t.Union[np.ndarray, t.Dict[str, np.ndarray]],
    ) -> Path:

        # get file from a file_key
        _file = self.path / file_key

        # if file exists raise error
        if _file.exists():
            raise e.code.NotAllowed(
                msgs=[
                    f"The file {_file} already exists so we cannot overwrite "
                    f"the file. Please delete it if possible."
                ]
            )

        # save numpy data
        if isinstance(npy_data, np.ndarray):
            util.npy_array_save(file=_file, npy_array=npy_data)
        elif isinstance(npy_data, dict):
            util.npy_record_save(file=_file, npy_record_dict=npy_data)
        else:
            raise e.code.CodingError(
                msgs=[
                    f"Unrecognized type of npy_data {type(npy_data)!r} for "
                    f"file_key={file_key!r}",
                    f"Expected numpy array or dict of numpy array"
                ]
            )

        # return
        return _file

    def create_pre_runner(self):

        # make sure that shape and dtype are properly overridden
        _shape_keys = list(self.shape.keys())
        _dtype_keys = list(self.dtype.keys())
        _keys = self.file_keys
        _shape_keys.sort()
        _dtype_keys.sort()
        _keys.sort()
        if _keys != _shape_keys:
            raise e.validation.NotAllowed(
                msgs=[
                    f"The file_keys and the keys of shape dict do not match",
                    {
                        'file_keys': _keys,
                        'shape_dict_keys': _shape_keys
                    },
                    f"Make sure to override property `shape` in class "
                    f"{self.__class__} appropriately."
                ]
            )
        if _keys != _dtype_keys:
            raise e.validation.NotAllowed(
                msgs=[
                    f"The file_keys and the keys of dtype dict do not match",
                    {
                        'file_keys': _keys,
                        'dtype_dict_keys': _dtype_keys
                    },
                    f"Make sure to override property `dtype` in class "
                    f"{self.__class__} appropriately."
                ]
            )

        # call super and return
        return super().create_pre_runner()

    def create_post_runner(
        self, *, hooked_method_return_value: t.List[Path]
    ):
        # ----------------------------------------------------------------01
        # load as memmaps
        _npy_memmaps = {}
        for file_key in self.file_keys:
            # load memmaps
            # Note that files should be created on the disk if everything is
            # fine but state_manager files will be not on the disk and hence
            # we cannot use `self.get_files()`.
            # Note we read in memmap mode as we need only meta info
            _npy_memmaps[file_key] = util.npy_load(self.path / file_key, memmap=True)

        # ----------------------------------------------------------------02
        # check shape, dtype
        # ----------------------------------------------------------------02.01
        # loop over all file keys
        _dtypes = self.dtype
        _shapes = self.shape
        for file_key in self.file_keys:
            # ------------------------------------------------------------02.02
            # get memmap for file key
            # Note that files should be created on the disk if everything is
            # fine but state_manager files will be not on the disk and hence
            # we cannot use `self.get_file()`. Hence we rely on `s.NpyMemMap`.
            _npy_memmap = _npy_memmaps[file_key]
            # ------------------------------------------------------------02.03
            # check dtype
            if _npy_memmap.dtype != _dtypes[file_key]:
                raise e.validation.NotAllowed(
                    msgs=[
                        f"Type mismatch for files created.",
                        f"The data type for loaded numpy file from disk for "
                        f"file_key `{file_key}` does not match.",
                        f"Expected {self.dtype[file_key]} but found "
                        f"{_npy_memmap.dtype}",
                        f"Check file path: {self.path}"
                    ]
                )
            # ------------------------------------------------------------02.03
            # check shape
            if _npy_memmap.shape != _shapes[file_key]:
                raise e.validation.NotAllowed(
                    msgs=[
                        f"Shape mismatch for files created.",
                        f"The shape for loaded numpy file from disk for "
                        f"file_key `{file_key}` does not match.",
                        f"Expected {_shapes[file_key]} but found "
                        f"{_npy_memmap.shape}"
                    ]
                )

        # ----------------------------------------------------------------03
        # delete memmaps ... so that it is quickly eligible for garbage
        # collection
        del _npy_memmaps

        # ----------------------------------------------------------------04
        # call super and return
        return super().create_post_runner(
            hooked_method_return_value=hooked_method_return_value)


@dataclasses.dataclass(frozen=True)
class TempFileGroup(FileGroup, abc.ABC):
    """
    Tuple to create temporary files .... note that when python terminates
    this object will automatically delete all temporary files ...
    todo: if you do not want for file to get deleted then have some option ....
      keep_file=True
    """

    # we should not override dunders
    # def __del__(self):
    #     """
    #     When object destroyed delete files automatically
    #     """
    #     # todo: find some awesome way to delete files .... or just report
    #     #  users of over usage ... write some code in HashableClass at class
    #     #  level to scan files in Temp folder and run interactive session to
    #     #  delete them
    #     ...


@dataclasses.dataclass(frozen=True)
class DownloadFileGroup(FileGroup, abc.ABC):
    """
    todo: although we retrieve files from urls we might sometimes
      need authentication ... and that is where the create must use
      `storage.file_system` so that files can be downloaded from anywhere

    todo: Explore `fsspec.implementations.cached` to cache files locally
      on first access
    """

    @property
    def file_system(self) -> str:
        return "DOWNLOAD"

    @property
    def name(self) -> str:
        # we assume that this will remain unique as we group by module name.
        # Note that this does mean that you cannot add fields to
        # DownloadFieldGroup
        return self.__class__.__name__

    @property
    @util.CacheResult
    def file_keys(self) -> t.List[str]:
        return list(self.get_urls().keys())

    @property
    @abc.abstractmethod
    def meta_info(self) -> dict:
        """
        Please try to return author provided hashes for future reference
        with dict key
        Example:
            {
                'author_hashes_type': 'md5',
                'author_hashes': {},
            }
        """
        ...

    @abc.abstractmethod
    def get_urls(self) -> t.Dict[str, str]:
        ...

    def create(self) -> t.List[Path]:
        """
        todo: we can make this with asyncio with aiohttps and aiofiles
          https://gist.github.com/darwing1210/c9ff8e3af8ba832e38e6e6e347d9047a
        """
        # ------------------------------------------------------ 01
        # get details
        _rp = self.richy_panel
        _total_files = len(self.file_keys)
        _rp.update(f"get content length for {_total_files} files")
        _chunk_size = 1024 * 50
        _file_paths = {
            fk: self.path/fk for fk in self.file_keys
        }  # type: t.Dict[str, Path]
        _urls = self.get_urls()
        _raise_error = False
        _errors = {}
        _responses = {}

        # ------------------------------------------------------ 02
        # get panels
        _rp.update(f"download {_total_files} files")
        _download_progress = richy.Progress.for_download_and_hashcheck(
            title="Download Files", tc_log=_LOGGER,
            box_type=richy.r_box.HORIZONTALS,
            border_style=richy.r_style.Style(color="cyan"),
            console=_rp.console,
        )
        _rp['download_progress'] = _download_progress

        # ------------------------------------------------------ 03
        # now add tasks
        for fk in self.file_keys:
            if _file_paths[fk].exists():
                _download_progress.add_task(
                    task_name=fk, total=_file_paths[fk].stat()['size']
                )
            else:
                _download_progress.add_task(
                    task_name=fk, total=None
                )

        # ------------------------------------------------------ 04
        # now download files
        # todo: can we do hash check while downloading is undergoing ???
        for fk in self.file_keys:
            # get the task
            _task = _download_progress.tasks[fk]
            # if already present just move forward
            if _file_paths[fk].exists():
                _task.already_finished()
                continue
            try:
                with _file_paths[fk].open('wb') as _f:
                    _response = requests.get(_urls[fk], stream=True)
                    try:
                        _length = int(_response.headers['content-length'])
                        _task.update(total=_length)
                    except Exception as _ee:
                        raise Exception("error getting content length: " + str(_ee))
                    for _chunk in _response.iter_content(
                        chunk_size=min(_length // 10, _chunk_size)
                    ):
                        if _chunk:  # filter out keep-alive new chunks
                            _f.write(_chunk)
                            _task.update(advance=len(_chunk),)
            except Exception as _exp:
                _errors[fk] = str(_exp)
                _raise_error = True

        # ------------------------------------------------------ 05
        # raise error if _raise_error
        if _raise_error:
            raise e.validation.NotAllowed(
                msgs=["Check errors ...", _errors]
            )

        # ------------------------------------------------------ 06
        # clean for richy
        _rp.update("finished downloading files")
        del _rp['download_progress']

        # ------------------------------------------------------ 07
        # return
        return list(_file_paths.values())

    # noinspection PyTypeChecker
    def create_file(self, *, file_key: str) -> Path:
        raise e.code.CodingError(
            msgs=[
                f"This method need not be called as create method is "
                f"overridden for class {self.__class__}"
            ]
        )


@dataclasses.dataclass(frozen=True)
class FileGroupFromPaths(FileGroup):
    """
    A concrete class that can convert any folder with files inside it to FileGroup
    Note that the folder should be inside a `Folder` given by field `parent_folder`
    """

    parent_folder: "folder.Folder"
    # the folder inside `parent_folder` which will have files given by `file_paths`
    # and will be converted to `FileGroup` by generating *.info and *.config files
    folder_name: str
    keys: t.List[str]

    @property
    def name(self) -> str:
        return self.folder_name

    @property
    def is_auto_hash(self) -> bool:
        return True

    @property
    @util.CacheResult
    def file_keys(self) -> t.List[str]:
        return self.keys

    @property
    def _uses_parent_folder(self) -> bool:
        return True

    @property
    def unknown_paths_on_disk(self) -> t.List[Path]:
        """
        As the files will already be created for this FileGroup we trick the system
        to ignore those already created files so that pre_runner checks can succeed
        """
        return [
            _f for _f in super().unknown_paths_on_disk
            if _f.name not in self.file_keys
        ]

    def create(self) -> t.List[Path]:

        _ret = []
        _rp = self.richy_panel
        _rp.update("creating file group from file paths")

        for fk in self.file_keys:
            _f = self.path / fk
            if not _f.exists():
                raise e.code.CodingError(
                    msgs=[
                        f"We were expecting path {_f} to exist"
                    ]
                )
            _ret.append(_f)

        return _ret

    # noinspection PyTypeChecker
    def create_file(self, *, file_key: str) -> Path:
        raise e.code.CodingError(
            msgs=[
                f"This method need not be called as create method is "
                f"overridden for class {self.__class__}"
            ]
        )
