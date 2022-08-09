import dataclasses
import typing as t

from .__base__ import StorageHashable
from .. import error as e
from .. import util
from .. import marshalling as m
from . import Suffix
from . import Path
from .. import richy
from .. import logger

_LOGGER = logger.get_logger()


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_not_to_be_overridden=['name'],
)
class Folder(StorageHashable):
    """
    A folder for hashable instance like Dataset or Model.

    Name of the folder:
      The name of folder is the name of the hashable it represents. The
      dataclass field `for_hashable` signifies the uniqueness of the folder
      while the `paren_folder` field super class does not affect uniqueness
      as the folder represented by this class is saved under it ;)

      Deviation from `HashableClass.name` behaviour:
        You might be thinking why not have have folder hex_hash as folder name.
        That sounds fine. But the name of folder using hashables name can in
        future let us use via external utilities to pick up folders only by
        knowing hashable and the path must be provided only once.
        Also parent_folder is required only to get parent folder info we can
        get away just by knowing the path.

      Note that for FileGroup the parent_folder is considered as they have
      even more fields and here we ignore parent_folder so that for_hashable
      decides the folder name

    We do not allow to add fields in subclass:
      In order that *.info files do not pollute with more info we do not
      allow to add fields to Folder class while subclassing.
      In case you want more info please use *.config file via Folder.config
      property

    The contains property:
      Indicates what will stored in this Folder

    When parent_folder is None override path
      This behaviour is borrowed from super class and well suits the
      requirement for Folder class

    Made up of three things
    + <hash>.info
      - when loaded gives out Folder object with hashable instance object
    + <hash>.config
      - the access info
    + <hash> folder
      - A folder inside which you can have folder's or file_group's
    """

    for_hashable: t.Union[str, m.HashableClass]

    @property
    def name(self) -> str:
        """
        Do not override.

        NOTE this also happens to be name of the folder

        Note that for Folder the uniqueness is completely decided by
        self.for_hashable field.

        If self.for_hashable is str then the user is not using hashable and
        simply wants to create folder with some specific name

        We use self.for_hashable.name as name of the folder. Remember that
        name is to be unique across hashable. By default the name returns
        hex_hash but when you override it to return string the user need to
        take care that it is unique for each instance of that class.

        Note that FileGroup considers parent_folder while creating name but
        here we ignore as there are no extra fields we will define here. Also
        we want fo_hashable to dictate things in Folder like the name of
        folder created on disk.
        """
        # the name is dictated by for_hashable as we will not allow any
        # fields in Folder (check validation)
        # This is unlike FileGroup where all fields decide name ... this si
        # because in FileGroup we intend to have more fields
        if isinstance(self.for_hashable, str):
            return self.for_hashable
        else:
            # the name defaults to hex_hash but if you have overridden it then
            # we assume you have taken care of creating unique name for all
            # possible instance of hashable class
            return self.for_hashable.name

    @property
    def is_created(self) -> bool:
        """
        This does mean we need call to create_all

        todo: maybe not that big of a overhead but try to check if call to
          this property is minimal
        """
        # ----------------------------------------------------------------01
        _folder_present = self.path.isdir()
        # (The super method is responsible to do this as state manager is
        # available)
        _state_manager_files_available = super().is_created

        # ----------------------------------------------------------------02
        # if _state_manager_files_available then folder must be present... the
        # vice versa is not necessary ... this is because when state manager
        # files are deleted we might still retain Folders as they hold
        # valuable files like download files, processed files, results etc.
        # NOTE: we do delete state files in cases when config and info files
        # are are modifies over new versions ... so we need to protect data
        # deletion
        if _state_manager_files_available:
            if not _folder_present:
                raise e.code.CodingError(
                    msgs=[
                        f"The state is available but respective folder is "
                        f"absent."
                    ]
                )

        # ----------------------------------------------------------------03
        # time to return
        return _state_manager_files_available

    @property
    def group_by(self) -> t.List[str]:
        """
        Default is use grouping from for_hashable as the storage will be controlled by
        that hashable class
        """
        if isinstance(self.for_hashable, str):
            return []
        return self.for_hashable.group_by

    def on_enter(self):
        # call super
        super().on_enter()

        # create
        if not self.is_created:
            self.create()

    def create(self) -> Path:
        """
        If there is no Folder we create an empty folder.
        """
        if not self.path.isdir():
            self.richy_panel.update(f"creating folder {self.name}")
            self.path.mkdir()

        # return
        return self.path

    def delete(self, *, force: bool = False) -> t.Any:
        _rp = self.richy_panel
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
            #     f"Do you want to delete files for Folder `{self.path}`?",
            #     default=True,
            # )

        # perform action
        if response == "y":
            _rp.update("deleting folder ...")
            for _sh in self.walk(only_names=False):
                with _sh(richy_panel=_rp):
                    _sh.delete(force=force)

        # todo: remove redundant check
        # by now we are confident that folder is empty so just check it
        if not self.path.is_dir_empty():
            raise e.code.CodingError(
                msgs=[
                    f"The folder should be empty by now ...",
                    f"Check path {self.path}",
                    f"May be you have non StorageHashable files ... note that even "
                    f"with force=True we cannot delete this"
                ]
            )

    def warn_about_garbage(self):
        """
        On disk a StorageHashable will have two files and one folder
        + folder <hashable_name>
        + file <hashable_name>.info
        + file <hashable_name>.config

        A walk on folder will give us all the StorageHashable.
        Anything else which do not have info and config will be treated as garbage
        and can be warned about it.

        todo: implement this

        """
        ...

    def walk(
        self, only_names: bool = True
    ) -> t.Iterable[t.Union[str, StorageHashable]]:
        """
        When only_names = True things will be fast

        Note that walk will not test if other components are present or not
        On disk a StorageHashable will have two files and one folder
        + folder <hashable_name>
        + file <hashable_name>.info
        + file <hashable_name>.config
        [NOTE]
        This method will only look for *.info files so be aware that if other files
        are not present this can falsely yield a StorageHashable
        """

        # -----------------------------------------------------------------01
        # track for registered file groups
        # *** NOTE ***
        # We skip anything that does not end with *.info this will also
        # skip files that are not StorageHashable .... but that is okay
        # for multiple reasons ...
        #  + performance
        #  + we might want something extra lying around in folders
        #  + we might have deleted state info but the folders might be
        #    lying around and might be wise to not delete it
        # The max we can do in that case is warn users that some
        # thing else is lying around in folder check method
        # warn_about_garbage.
        _sep = self.path.sep
        if only_names:
            for f in self.path.glob(pattern=f"*{Suffix.info}"):
                yield f.full_path.split(_sep)[-1].split(f"{Suffix.info}")[0]
        else:
            for f in self.path.glob(pattern=f"*{Suffix.info}"):
                # build instance
                _cls = m.YamlRepr.get_class(f)
                # noinspection PyTypeChecker
                _hashable = _cls.from_yaml(
                    f, parent_folder=self,
                )  # type: StorageHashable
                # yield
                yield _hashable

        # -----------------------------------------------------------------02
        # todo: we might not need this as we are yielding above ... delete later
        # sync is equivalent to accessing folder
        # so update state manager files
        # self.config.append_last_accessed_on()
