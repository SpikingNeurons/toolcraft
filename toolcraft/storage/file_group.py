"""
All we extend StorageHashable to save files

todo: add support for keepsake for saving blobs
  https://github.com/replicate/keepsake
  This library is very simple but may be we can do better storage or may be
  we add more fields to their existing proto buffers

"""

import sys
import typing as t
import pathlib
import dataclasses
import abc
import numpy as np
import gc
import datetime
import random

from .. import util, logger, settings
from .. import storage as s
from .. import error as e
from . import StorageHashable

_LOGGER = logger.get_logger()

SHUFFLE_SEED_TYPE = t.Union[
    t.Literal[
        'DETERMINISTIC_SHUFFLE',
        'NO_SHUFFLE',
        'DO_NOT_USE',
        'NON_DETERMINISTIC_SHUFFLE',
    ],
    np.ndarray,
]
# noinspection PyUnresolvedReferences
DETERMINISTIC_SHUFFLE = SHUFFLE_SEED_TYPE.__args__[0].__args__[0]
# noinspection PyUnresolvedReferences
NO_SHUFFLE = SHUFFLE_SEED_TYPE.__args__[0].__args__[1]
# noinspection PyUnresolvedReferences
DO_NOT_USE = SHUFFLE_SEED_TYPE.__args__[0].__args__[2]
# noinspection PyUnresolvedReferences
NON_DETERMINISTIC_SHUFFLE = SHUFFLE_SEED_TYPE.__args__[0].__args__[3]

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
            _delta_time = datetime.datetime.now() - _last_check_time
            return int(_delta_time.total_seconds()) > \
                self.check_interval_choice

    # noinspection DuplicatedCode
    def append_checked_on(self):
        # this can never happen
        if len(self.checked_on) > self.LITERAL.checked_on_list_limit:
            e.code.CodingError(
                msgs=[
                    f"This should never happens ... did you try to append "
                    f"checked_on list multiple times"
                ]
            )
        # limit the list
        if len(self.checked_on) == self.LITERAL.checked_on_list_limit:
            self.checked_on = self.checked_on[1:]
        # append time
        self.checked_on.append(datetime.datetime.now())


@dataclasses.dataclass(frozen=True)
class FileGroupResultsFolder(s.ResultsFolder):

    class LITERAL(s.ResultsFolder.LITERAL):
        results_folder_name = "_results"

    for_hashable: "FileGroup"

    @property
    def name(self) -> str:
        return self.LITERAL.results_folder_name

    @property
    @util.CacheResult
    def root_dir(self) -> pathlib.Path:
        return self.for_hashable.path


@dataclasses.dataclass(frozen=True)
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
            path_prefix=self.path.as_posix(),
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
            f.is_file() or f.is_dir()
            for f in [
                self.path / fk for fk in self.file_keys
            ]
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

                e.code.CodingError(
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
    def unknown_files_on_disk(self) -> t.List[pathlib.Path]:

        # container for unknown files
        _unknown_files = []

        # look inside path dir if it exists
        if self.path.exists():
            # expect path to be a dir
            if self.path.is_file():
                e.code.CodingError(
                    msgs=[
                        f"We expect path to be a dir for FileGroup"
                    ]
                )
            # look inside path dir
            for f in self.path.iterdir():
                if f.name in self.file_keys and f.is_file():
                    continue
                if f.name.startswith(
                    FileGroupResultsFolder.LITERAL.results_folder_name
                ):
                    continue
                _unknown_files.append(f)

        # return
        return _unknown_files

    @property
    def is_auto_hash(self) -> bool:
        return False

    @property
    def periodic_check_needed(self) -> bool:

        # if file creation needed do not call this method
        # todo: remove later
        if not self.is_created:
            e.code.CodingError(
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

    @property
    @util.CacheResult
    def results_folder(self) -> FileGroupResultsFolder:
        return FileGroupResultsFolder(
            for_hashable=self,
        )

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
                e.code.CodingError(
                    msgs=[
                        f"Never call this until files are created. Only after "
                        f"that the state files will be present on the disk"
                    ]
                )

            # check if auto_hashes present
            if self.config.auto_hashes is None:
                e.code.CodingError(
                    msgs=[
                        f"We expect that auto_hashes will be set by now"
                    ]
                )

            # return
            return self.config.auto_hashes

        # if not auto hash then raise error to inform to override this method
        else:
            e.code.NotAllowed(
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
            # useless return
            return {}

    @classmethod
    def hook_up_methods(cls):
        # call super
        super().hook_up_methods()

        # hook up get
        util.HookUp(
            cls=cls,
            silent=True,
            method=cls.check,
            pre_method=cls.check_pre_runner,
            post_method=cls.check_post_runner,
        )

        # hook up get
        util.HookUp(
            cls=cls,
            silent=True,
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
                e.code.CodingError(
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
                e.code.CodingError(
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
                )
                # This is in case we want to let code print hash that we want
                # to supply
                # value should be a valid hash
                # if not len(_hash) == 64:
                #     e.code.NotAllowed(
                #         msgs=[
                #             f"Unsupported file hash for key {k!r}",
                #             f"We only support sha-256",
                #             f"Found hash {_hash!r} with length "
                #             f"{len(_hash)!r}"
                #         ]
                #     )
                # check if value is lower case
                if _hash.lower() != _hash:
                    e.code.NotAllowed(
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
                    e.code.CodingError(
                        msgs=[
                            f"Please provide hash for file_key `{k}` in "
                            f"`get_hashes` method of class {self.__class__}"
                        ]
                    )

        # ---------------------------------------------------------- 04
        # check if duplicate file_keys
        if len(self.file_keys) != len(set(self.file_keys)):
            e.validation.NotAllowed(
                msgs=[
                    f"We found some duplicates in self.file_keys",
                    self.file_keys
                ]
            )

        # ---------------------------------------------------------- 05
        # check if files used in this file group can be handled for disk io
        for f in [self.path / fk for fk in self.file_keys]:
            e.io.LongPath(path=f, msgs=[])

    def init(self):
        # ----------------------------------------------------------- 01
        # call super
        super().init()

        # ----------------------------------------------------------- 02
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
                e.code.CodingError(
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

        # ----------------------------------------------------------- 03
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

    def check_pre_runner(self, *, force: bool = False):
        # ~~~~~~~~~~~~ special check ~~~~~~~~~ to avoid coding bugs
        # Although redundant it helps avoid unnecessary calls to check ...
        # Example in case of FileGroup we can avoid long time consuming checks.
        # The check() must be called only needed to catch some coding errors we
        # do this
        if not self.is_created:
            e.code.CodingError(
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
                e.code.CodingError(
                    msgs=[
                        f"Find the bug in the code, you need to make sure if "
                        f"periodic check is needed using property "
                        f"self.periodic_check_needed then only call this "
                        f"function"
                    ]
                )

    # noinspection PyUnusedLocal
    def check(self, *, force: bool = False):

        _failed_hashes = util.crosscheck_hashes_for_paths(
            paths={fk: self.path / fk for fk in self.file_keys},
            hash_type='sha256',
            correct_hashes=self.get_hashes(),
            msg=f"file group `{self.name}`"
        )

        if bool(_failed_hashes):
            # wipe state manager files
            self.info.delete()
            self.config.delete()
            # raise error
            e.code.CodingError(
                msgs=[
                    f"Hashes for some files did not match. ",
                    f"FileGroup: {self.name}",
                    f"Check below",
                    _failed_hashes
                ]
            )

    # noinspection PyUnusedLocal
    def check_post_runner(
        self, *, hooked_method_return_value: t.Any
    ):

        # since things are now checked write to disk but before that make
        # sure to add checked on info
        self.config.append_checked_on()
        ...

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
                e.code.CodingError(
                    msgs=[
                        f"The supplied `file_key={file_key}` to "
                        f"`{self.__class__}.get_file` method is not one of:",
                        self.file_keys
                    ]
                )

        # --------------------------------------------------------------02
        # check if created
        if not self.is_created:
            e.validation.NotAllowed(
                msgs=[
                    f"Make sure to create files for instance of type "
                    f"{self.__class__} before calling `get_files()`"
                ]
            )

        # --------------------------------------------------------------03
        # if periodic check needed
        if self.periodic_check_needed:
            e.validation.NotAllowed(
                msgs=[
                    f"Make sure to perform check before using `get_file()` "
                    f"for class {self.__class__}"
                ]
            )

        # --------------------------------------------------------------04
        # delete if outdated
        if self.is_outdated:
            e.validation.NotAllowed(
                msgs=[
                    f"Files are out dated for class {self.__class__}. You "
                    f"need to delete it."
                ]
            )

    @abc.abstractmethod
    def get_files(
        self, *,
        file_keys: t.List[str]
    ) -> t.Dict[str, t.Any]:
        """
        Note we return t.Any as you can return anything like file path
        numpy array record etc.
        """
        ...

    # noinspection PyUnusedLocal
    def get_files_post_runner(
            self, *, hooked_method_return_value: t.Dict[str, t.Any]
    ):
        # --------------------------------------------------------------01
        # we are getting data so update the access info
        self.config.append_last_accessed_on()

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
        _unknown_files = self.unknown_files_on_disk
        if bool(_unknown_files):
            e.code.NotAllowed(
                msgs=[
                    f"We were trying to create files for class "
                    f"{self.__class__.__name__!r} with base name "
                    f"{self.name!r} in dir `{self.path}` but, we "
                    f"found below unknown files",
                    [f.name for f in _unknown_files]
                ]
            )

    def create(self) -> t.List[pathlib.Path]:
        _ret = []

        # some variables to indicate progress
        # todo: make it like progress bar
        _total_files = len(self.file_keys)
        _s_fmt = len(str(_total_files))
        spinner = self.spinner
        for i, k in enumerate(self.file_keys):
            # get expected file from key
            _expected_file = self.path / k

            # log
            spinner.text = f"{_expected_file.name!r}: " \
                           f"{i + 1: {_s_fmt}d}/{_total_files} created ..."

            # if found on disk bypass creation for efficiency
            if _expected_file.is_file():
                _ret.append(_expected_file)
                continue

            # if expected file not present then create
            _created_file = _expected_file if _expected_file.exists() else \
                self.create_file(file_key=k)

            # if check if created and expected file is same
            if _expected_file != _created_file:
                e.code.CodingError(
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
            self, *, hooked_method_return_value: t.List[pathlib.Path]
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
            e.code.CodingError(
                msgs=[
                    f"Expected a list from {self.__class__.create_file} but "
                    f"instead found returned value of type "
                    f"{type(created_fs)}"
                ]
            )
        # ----------------------------------------------------------------01.02
        # check if created file is proper and if it is on disk
        for f in created_fs:
            if not isinstance(f, pathlib.Path):
                e.code.CodingError(
                    msgs=[
                        f"Method {self.create_file} should return the list of "
                        f"files crested, instead found {created_fs}"
                    ]
                )
            if f not in expected_fs:
                e.code.CodingError(
                    msgs=[
                        f"File {f.name!r} generated by create method of class "
                        f"{self.__class__} does not correspond to one of the "
                        f"file keys given by property self.file_keys",
                        self.file_keys
                    ]
                )
            if not f.exists():
                e.code.CodingError(
                    msgs=[
                        f"One of the file {f} you are returning from "
                        f"self.create_file() is not present on the disk"
                    ]
                )
            e.io.LongPath(path=f, msgs=[])
        # ----------------------------------------------------------------01.03
        # check if all key_paths i.e expected files are generated
        for f in expected_fs:
            if f not in created_fs:
                e.code.CodingError(
                    msgs=[
                        f"We expect file {f.name} to be created",
                        f"But the file was not created"
                    ]
                )

        # ----------------------------------------------------------------02
        # if unknown files present throw error
        _unknown_files = self.unknown_files_on_disk
        if bool(_unknown_files):
            e.code.NotAllowed(
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
        for f in created_fs:
            util.io_make_path_read_only(f)

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
                e.code.CodingError(
                    msgs=[
                        f"We just generated files so we do not expect auto "
                        f"hashes to be present in the config"
                    ]
                )
            _auto_hashes = util.crosscheck_hashes_for_paths(
                paths={k: self.path/k for k in self.file_keys},
                hash_type='sha256',
                msg=f"file group {self.name}",
                correct_hashes=None,
            )
            self.config.auto_hashes = _auto_hashes

        # ----------------------------------------------------------------06
        # return
        return _ret

    @abc.abstractmethod
    def create_file(self, *, file_key: str) -> pathlib.Path:
        """
        If for efficiency you want to create multiple files ... hack it to
        create files on first call and subsequent file_keys will just fake
        things to return path.

        Note: create can only return file path and nothing else
        """
        ...

    def delete(self, *, force: bool = False):
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
        if settings.FileHash.DEBUG_HASHABLE_STATE:
            # if config.DEBUG_HASHABLE_STATE we know what we are doing ... we
            # are debugging and there will be one time programmatically delete
            # so set the response automatically for FileGroup
            force = True
            # just let us warn user
            _last_spinner = self.spinner
            _last_spinner.stop()
            _LOGGER.warning(
                msg=f"Deleting files automatically for file group "
                    f"{self.__class__.__name__!r}",
                msgs=[
                    f"name: {self.name!r}",
                    f"path: {self.path}",
                    f"This is intentional as you have set "
                    f"`config.DEBUG_HASHABLE_STATE = True`"
                ]
            )
            _last_spinner.start()

        # ---------------------------------------------------------------02
        # delete
        # We ask for user response as most of the files/folders are important
        # and programmatically deletes will cost download or generation of
        # files ...
        # This can be easily bypasses by setting force == True
        if force:
            response = "y"
        else:
            _formatted_names = "".join(
                [
                    f"\t > file: {p.name}\n"
                    for p in [
                        self.path / fk for fk in self.file_keys
                    ]
                ]
            )
            _last_spinner = self.spinner
            _last_spinner.stop()
            response = util.input_response(
                question=f"Do you really want to delete the listed "
                         f"files/folders for file group {self.name!r} in "
                         f"path {self.path} ???\n"
                         f"{_formatted_names}\n",
                options=["y", "n"]
            )
            _last_spinner.start()

        # ---------------------------------------------------------------03
        # perform action
        if response == "y":

            # -----------------------------------------------------------03.01
            # some variables to indicate progress
            # todo: make it like progress bar
            _total_keys = len(self.file_keys)
            _s_fmt = len(str(_total_keys))
            spinner = self.spinner

            # -----------------------------------------------------------03.02
            # delete all files for the group
            for i, fk in enumerate(self.file_keys):

                _key_path = self.path / fk

                spinner.text = f"{_key_path.name!r}: " \
                               f"{i: {_s_fmt}d}/{_total_keys} deleted ..."

                if _key_path.is_file() or _key_path.is_dir():
                    util.io_path_delete(_key_path, force=force)
                else:
                    e.code.CodingError(
                        msgs=[
                            f"If you deleted files manually this can happen",
                            f"But if you didnt then this might be a bug",
                            f"We were not able to find file group with path "
                            f"{_key_path}"
                        ]
                    )

            # -----------------------------------------------------------03.03
            # delete results folder as most likely we will not need it
            # todo: if you want to retain the items inside this folder odify
            #  this code
            self.results_folder.delete(force=force)
        else:
            e.code.ExitGracefully(
                msgs=[
                    "We will terminate the program as you requested "
                    "not to delete files..."
                ]
            )
            # just in case when in debug or testing if error module
            # is configured for raising instead of exiting
            sys.exit()

            # just in case exit does not exit
            # noinspection PyUnreachableCode
            raise


# noinspection PyArgumentList
class NpyMemMap:
    """
    Wrapper class used to add features on top on memmap we read from disk.

    We provide features like:
    + Shuffle
        When shuffle is True the entire data on disk is accessed in random
        way with fixed SEED so that you can fetch data partially or completely.
        Note that you can always access data that will not be shuffled via
        self.memmap ... in case you want to read huge memmap's for debugging
        and do not want shuffling behaviour

    todo: we can support in future support multiple NpyMemMap files with
      shuffle where multiple NpyMemMap's can be accessed randomly with with
      the elements internal to them are again accessed randomly
    """

    def __init__(
        self,
        file_path: pathlib.Path,
    ):
        """

        Args:
            file_path: The numpy file path
        """
        # ------------------------------------------------------------ 01
        # save args passed
        self.file_path = file_path
        # check if file_path exists
        if not file_path.is_file():
            e.io.FileMustBeOnDiskOrNetwork(
                path=file_path,
                msgs=[]
            )

        # ------------------------------------------------------------ 02
        # load memmap temporarily here to set some useful vars
        # noinspection PyTypeChecker
        memmap = np.load(file_path, mmap_mode="r")
        # ------------------------------------------------------------ 02.01
        # shape
        self.shape = memmap.shape
        # ------------------------------------------------------------ 02.02
        # dtype
        self.dtype = memmap.dtype
        # ------------------------------------------------------------ 02.03
        # ndim
        self.ndim = memmap.ndim

        # ------------------------------------------------------------ 03
        # delete memmap so that there are no open references that cause
        # windows permission error
        del memmap
        # also garbage collect as del alone does not work
        # https://stackoverflow.com/questions/39953501/i-cant-remove-file\-created-by-memmap
        gc.collect()

    def __len__(self) -> int:
        return self.shape[0]

    def __iter__(self) -> np.ndarray:
        return self[:]

    def __getitem__(
        self,
        item: t.Union[
            SELECT_TYPE,
            t.Tuple[
                SELECT_TYPE, ...
            ]
        ]
    ) -> np.ndarray:
        """

        todo: Performance analysis of randomly accessing numpy mem maps
          this cab be slow on linux .... also check if it is fast for
          windows ...
          refer issue here https://github.com/numpy/numpy/issues/13172

        todo: if slow make async fetch so that next batch is ready in advance
          or else make a buffer where a parallel thread will fill up batches

        """
        # ---------------------------------------------------------- 01
        # if call_helper attribute not there raise error
        try:
            _call_helper = self.call_helper
        except AttributeError:
            e.code.CodingError(
                msgs=[
                    f"When using with statement make sure to call __call__ "
                    f"method so that call_helper attribute is available."
                ]
            )
            raise AttributeError()

        # ---------------------------------------------------------- 02
        # if do_not_use raise error
        if _call_helper.do_not_use:
            e.code.NotAllowed(
                msgs=[
                    f"You opted do_not_use=True hence you cannot use "
                    f"__getitem__ method",
                ]
            )

        # ---------------------------------------------------------- 03
        # if single valued memmap then make sure that item is USE_ALL and
        # return ... no need to check for shuffle indices
        if len(_call_helper.memmap) == 1:
            if item != USE_ALL:
                e.code.CodingError(
                    msgs=[
                        f"For sanity we force you to use `:` while indexing "
                        f"NpyMemMap's with single value",
                        f"This allows to make sure that things are as "
                        f"intended while accessing with shuffled indices"
                    ]
                )
            return _call_helper.memmap[USE_ALL]

        # ---------------------------------------------------------- 03
        # adapt item if is_shuffled
        if _call_helper.is_shuffled:
            if isinstance(item, (int, slice, list, np.ndarray)):
                # get shuffled indices
                item = _call_helper.shuffle_indices[item]
            elif isinstance(item, tuple):
                # get shuffled indices
                if isinstance(item[0], (int, slice, list, np.ndarray)):
                    item = (_call_helper.shuffle_indices[item[0]], *item[1:])
                else:
                    e.code.CodingError(
                        msgs=[
                            f"First element of tuple is not a int or slice "
                            f"instead found type {type(item[0])}"
                        ]
                    )
            else:
                e.code.CodingError(
                    msgs=[
                        f"The item can be int, slice or tuple instead found "
                        f"type {type(item)}"
                    ]
                )

        # ---------------------------------------------------------- 04
        # return
        # ---------------------------------------------------------- 04.01
        # return memmap if all samples selected and there was no shuffling
        # if None slice i.e. all elements accessed why not return memmap as
        # it is ... note that in case if there is shuffle
        # i.e. _call_helper.is_shuffled=True the code at comment 03 will have
        # anyways converted it to ndarray so we can safely return memmap here
        if item is USE_ALL:
            # todo: remove this assert statement once you are sure
            e.code.AssertError(
                value1=_call_helper.is_shuffled,
                value2=False,
                msgs=[
                    f"Some coding error we are sure that the NpyMemMap is "
                    f"opened with `shuffle_seed=NO_SHUFFLE`"
                ]
            )
            return _call_helper.memmap
        # ---------------------------------------------------------- 04.02
        # if anything else then we need to read memmap
        # todo: see if more optimization can be done so that memmaps are not
        #  loaded in memory ... like may be try caching what is read etc.
        elif isinstance(item, tuple):
            # this surprising code is needed if you end up using list of ints
            # example ...
            # noinspection PyTypeChecker
            return _call_helper.memmap[
                # this one is first dimension and works on memmap mostly used
                # for shuffling
                item[0]
            ][
                # remaining items ... note that slice(None, None, None) is
                # used to select all elements after applying index item[0]
                (USE_ALL, *item[1:])
            ]
        else:
            return _call_helper.memmap[item]

    def __call__(
        self,
        shuffle_seed: SHUFFLE_SEED_TYPE,
    ):

        # check if already called
        try:
            # noinspection PyUnresolvedReferences
            _ = self.call_helper
            # we do not expect attribute call_helper here
            e.code.CodingError(
                msgs=[
                    f"Call was already called on the NpyMemmap instance.",
                    f"To avoid this you need to call __call__ with "
                    f"help of `with` statement.",
                    f"Also please check if the iterator opened using __call__ "
                    f"is properly exhausted"
                ]
            )
        except AttributeError:
            # pass that's what we want
            ...

        # make instance of call_helper
        self.call_helper = NpyMemMapCallHelper(
            npy_memmap=self,
            shuffle_seed=shuffle_seed,
        )

        # return self
        return self

    def __enter__(self):
        # if call_helper attribute not there raise error
        try:
            _ = self.call_helper
        except AttributeError:
            e.code.CodingError(
                msgs=[
                    f"When using with statement make sure to call __call__ "
                    f"method so that call_helper attribute is available."
                ]
            )

        # return self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        todo handle exc_type, exc_val, exc_tb args for exception

        We implement this method as when memmap is done over files
        they are not released and numpy can only release those files after
        garbage collection. Check the discussion at
        https://stackoverflow.com/questions/39953501/i-cant-remove-file-created-by-memmap

        So what we do here is when the instance of this class is deleted we
        delete memmap and do garbage collection
        """
        # if call_helper attribute not there raise error
        try:
            _ = self.call_helper
        except AttributeError:
            e.code.CodingError(
                msgs=[
                    f"When using with statement make sure to call __call__ "
                    f"method so that call_helper attribute is available."
                ]
            )
        # reset
        del self.call_helper
        gc.collect()

    def __del__(self):
        # the call_helper attribute must not be present
        try:
            _ = self.call_helper
            # we do not expect attribute call_helper here
            e.code.CodingError(
                msgs=[
                    f"May be you have not exited properly from within with "
                    f"statement.",
                    f"We expect call_helper attribute to be deleted by now",
                    f"To avoid this you need to call __call__ with "
                    f"help of `with` statement."
                ]
            )
        except AttributeError:
            # pass that's what we want
            ...

    def min(self) -> t.Union[int, float]:
        # noinspection PyTypeChecker
        return np.load(self.file_path, mmap_mode="r").min()

    def max(self) -> t.Union[int, float]:
        # noinspection PyTypeChecker
        return np.load(self.file_path, mmap_mode="r").max()

    def get_raw_memmap(self) -> np.ndarray:
        # call_helper attribute must be present
        try:
            call_helper = self.call_helper
        except AttributeError:
            e.code.CodingError(
                msgs=[
                    f"We expect you to use `with` statement and make sure to "
                    f"call __call__ method on it"
                ]
            )
            raise AttributeError()

        # make sure that do_not_use is set
        if not call_helper.do_not_use:
            e.code.CodingError(
                msgs=[
                    f"You are using method {self.get_raw_memmap} and we "
                    f"expect you to set `shuffle_seed=s.DO_NOT_USE` as you "
                    f"want to use underlying memmap directly"
                ]
            )

        # return
        return self.call_helper.memmap

    def random_examples(
        self,
        num_examples: int,
    ) -> np.ndarray:
        """

        Note we do not use __getitem__ as it considers is_shuffled and will
        use shuffled indices

        Role of this method is to just extract arbitrary samples

        """
        # call_helper attribute must be present
        try:
            call_helper = self.call_helper
        except AttributeError:
            e.code.CodingError(
                msgs=[
                    f"We expect you to use `with` statement and make sure to "
                    f"call __call__ method on it"
                ]
            )
            raise AttributeError()

        # make sure that do_not_use is set
        if not call_helper.do_not_use:
            e.code.CodingError(
                msgs=[
                    f"You are using method {self.random_examples} and we "
                    f"expect you to set `shuffle_seed=s.DO_NOT_USE` as we will "
                    f"access underlying memmap directly"
                ]
            )

        # get sample indices
        np.random.seed(None)  # resets seed ... makes it non deterministic
        _sample_indices = np.random.randint(0, len(self), num_examples)

        # return
        return call_helper.memmap[_sample_indices]


class NpyMemMapCallHelper:

    @property
    def is_shuffled(self) -> bool:
        return hasattr(self, 'shuffle_indices')

    def __init__(
        self,
        npy_memmap: NpyMemMap,
        shuffle_seed: SHUFFLE_SEED_TYPE,
    ):
        # get memmap and length
        # noinspection PyTypeChecker
        self.memmap = np.load(npy_memmap.file_path, mmap_mode="r")
        self.do_not_use = (str(shuffle_seed) == DO_NOT_USE)

        # if length is 1 we cannot do any shuffle as the file may for single
        # element and as such we need not do anything
        _len = len(npy_memmap)
        if _len == 1:
            return

        # if DO_NOT_USE then return ... as no shuffle indices will be used
        if self.do_not_use:
            return

        # if NO_SHUFFLE return and there will be no shuffle indices
        if str(shuffle_seed) == NO_SHUFFLE:
            return

        # if np.ndarray then check shape
        if isinstance(shuffle_seed, np.ndarray):
            if not np.array_equal(
                np.unique(shuffle_seed),
                np.arange(_len, dtype=shuffle_seed.dtype)
            ):
                e.code.CodingError(
                    msgs=[
                        f"While supplying shuffle seed as shuffle indices "
                        f"make sure that it has all values from 0 to {_len}",
                        f"That is it must be a valid indices array that can "
                        f"index entire underlying numpy memmap"
                    ]
                )
            self.shuffle_indices = shuffle_seed
            return

        # if DETERMINISTIC_SHUFFLE reassign it with deterministic seed
        if str(shuffle_seed) in [
            DETERMINISTIC_SHUFFLE, NON_DETERMINISTIC_SHUFFLE
        ]:
            if str(shuffle_seed) == NON_DETERMINISTIC_SHUFFLE:
                shuffle_seed = None
            if str(shuffle_seed) == DETERMINISTIC_SHUFFLE:
                shuffle_seed = 259746  # some arbitrary number
            np.random.seed(shuffle_seed)
            self.shuffle_indices = np.random.permutation(_len)
            np.random.seed(None)
            return

        # should not happen as above cases should handle everything
        e.code.CodingError(
            msgs=[
                f"Not able to process shuffle_seed {shuffle_seed}"
            ]
        )

    def __del__(self):
        del self.memmap
        if not self.do_not_use:
            if self.is_shuffled:
                del self.shuffle_indices


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
            k: len(v) for k, v in self.all_npy_mem_maps_cache.items()
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

    @property
    @util.CacheResult
    def all_npy_mem_maps_cache(self) -> t.Dict[str, NpyMemMap]:
        """
        Used to cache NpyMemMap instances to avoid creating them again and
        again.
        """
        _ret = {}
        with logger.ProgressBar(
            iterable=self.file_keys, unit=" files", desc="Loading NpyMemMap's"
        ) as _pg:
            for fk in _pg:
                _ret[fk] = NpyMemMap(file_path=self.path / fk,)
        return _ret

    # noinspection PyMethodOverriding
    def __call__(
        self, *,
        shuffle_seed: SHUFFLE_SEED_TYPE,
    ) -> "NpyFileGroup":
        # call super
        # noinspection PyTypeChecker
        return super().__call__(
            # Note that we do not use iterating feature so set to None as we
            # need to satisfy the API requirement
            iter_show_progress_bar=None,
            iter_desc=None,
            iter_num_parts=None,
            iter_for_part=None,
            shuffle_seed=shuffle_seed
        )

    def on_enter(self):
        # call super
        super().on_enter()

        # get kwargs passed in call
        shuffle_seed = \
            self.internal.on_call_kwargs[
                'shuffle_seed'
            ]  # type: SHUFFLE_SEED_TYPE

        # get property
        _all_npy_mem_maps_cache = self.all_npy_mem_maps_cache

        # make NpyMemmaps aware of seed
        with logger.ProgressBar(
            iterable=self.file_keys, unit=" files", desc="Opening NpyMemMap's"
        ) as _pg:
            for k in _pg:
                v = _all_npy_mem_maps_cache[k]
                v(shuffle_seed=shuffle_seed)
                v.__enter__()

    def on_exit(self):
        # call super
        super().on_exit()

        # exit numpy memmaps
        # We have opened up all NpyMemMap's with shuffle_seed='DO_NOT_USE' ...
        # for use within `with` context ... so now we close it
        with logger.ProgressBar(
            iterable=self.file_keys, unit=" files", desc="Closing NpyMemMap's"
        ) as _pg:
            _pg.set_description(f"Closing NpyMemMap's")
            for k in _pg:
                v = self.all_npy_mem_maps_cache[k]
                # noinspection PyUnresolvedReferences
                v.__exit__(None, None, None)

    def get_files(
        self, *, file_keys: t.List[str]
    ) -> t.Dict[str, NpyMemMap]:
        # get spinner
        _spinner = logger.Spinner.get_last_spinner()

        # if spinner is None
        if _spinner is None:
            e.code.CodingError(
                msgs=[
                    f"We recently added spinner support so we expect that "
                    f"get_files method is called from with with context of "
                    f"active Spinner ..."
                ]
            )

        # container
        _ret = {}

        # loop over all files
        _num_files = len(file_keys)
        for i, file_key in enumerate(file_keys):
            # log
            _spinner.text = f"{(i+1):03d}/{_num_files:03d} fetching file" \
                            f" {file_key}"

            # get data
            _data = NpyMemMap(file_path=self.path / file_key,)

            # redundant check ... this was anyways checked while file creation
            # exists here for extra safety
            if len(_data) != self.shape[file_key][0]:
                e.code.CodingError(
                    msgs=[
                        f"This must be same and should be already checked in "
                        f"{self.__class__.create_post_runner}",
                        {
                            "file_key": file_key,
                            "found_shape": _data.shape,
                            "expected_shape": self.shape[file_key],
                        },
                        f"Check class {self.__class__}"
                    ]
                )

            # store data in container
            _ret[file_key] = _data

        # return
        return _ret

    def save_npy_data(
        self,
        file_key: str,
        npy_data: t.Union[np.ndarray, t.Dict[str, np.ndarray]],
    ) -> pathlib.Path:
        # get spinner and log
        _s = logger.Spinner.get_last_spinner()
        if _s is not None:
            _s.text = f"Saving numpy data for `{file_key}`"

        # get file from a file_key
        _file = self.path / file_key

        # if file exists raise error
        if _file.exists():
            e.code.NotAllowed(
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
            e.code.CodingError(
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
            e.validation.NotAllowed(
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
            e.validation.NotAllowed(
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
        self, *, hooked_method_return_value: t.List[pathlib.Path]
    ):
        # ----------------------------------------------------------------01
        # load as memmaps
        _npy_memmaps = {}
        for file_key in self.file_keys:
            # load memmaps
            # Note that files should be created on the disk if everything is
            # fine but state_manager files will be not on the disk and hence
            # we cannot use `self.get_file()`. Hence we rely on `s.NpyMemMap`.
            _npy_memmaps[file_key] = NpyMemMap(
                file_path=self.path / file_key,
            )

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
                e.validation.NotAllowed(
                    msgs=[
                        f"Type mismatch for files created.",
                        f"The data type for loaded numpy file from disk for "
                        f"file_key `{file_key}` does not match.",
                        f"Expected {self.dtype[file_key]} but found "
                        f"{_npy_memmap.dtype}"
                    ]
                )
            # ------------------------------------------------------------02.03
            # check shape
            if _npy_memmap.shape != _shapes[file_key]:
                e.validation.NotAllowed(
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

    @property
    @util.CacheResult
    def root_dir(self) -> pathlib.Path:
        return settings.Dir.TEMPORARY

    def get_files(
            self, *, file_keys: t.List[str]
    ) -> t.Dict[str, pathlib.Path]:
        return {
            file_key: self.path / file_key
            for file_key in file_keys
        }

    def get_file(self, file_key: str) -> pathlib.Path:
        return self.get_files(file_keys=[file_key])[file_key]

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
    @util.CacheResult
    def root_dir(self) -> pathlib.Path:
        return settings.Dir.DOWNLOAD

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

    @classmethod
    def block_fields_in_subclasses(cls) -> bool:
        return True

    @abc.abstractmethod
    def get_urls(self) -> t.Dict[str, str]:
        ...

    def create(self) -> t.List[pathlib.Path]:

        _file_paths = {
            fk: self.path/fk for fk in self.file_keys
        }
        _urls = self.get_urls()

        util.download_files(
            paths=_file_paths, urls=_urls, msg=f"file group `{self.name}`"
        )

        return list(_file_paths.values())

    # noinspection PyTypeChecker
    def create_file(self, *, file_key: str) -> pathlib.Path:
        e.code.CodingError(
            msgs=[
                f"This method need not be called as create method is "
                f"overridden for class {self.__class__}"
            ]
        )

    def get_files(
        self, *, file_keys: t.List[str]
    ) -> t.Dict[str, pathlib.Path]:
        return {
            file_key: self.path / file_key
            for file_key in file_keys
        }

    def get_file(self, file_key: str) -> pathlib.Path:
        return self.get_files(file_keys=[file_key])[file_key]


@dataclasses.dataclass(frozen=True)
class GitDownload(DownloadFileGroup, abc.ABC):
    """
    todo: Make this concrete ... see the SO question below
     https://stackoverflow.com/questions/791959/download-a-specific-tag-with-git
     What we aim is to get any archive based on tag and commit and save it as
     downloaded zip file ... this will help people to get downloads from
     public sources and migrate zips behind firewall...
     Also check:
      https://gitpython.readthedocs.io/
    """
    # tag: str  # or may be commit id
    # git_base_url: str
    ...
