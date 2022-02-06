import dataclasses
import typing as t

from .__base__ import StorageHashable
from .. import error as e
from .. import util
from .. import marshalling as m
from . import Suffix
from . import Path


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['items'],
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
    def contains(self) -> t.Union[
        t.Any, t.Type[StorageHashable]
    ]:
        """
        You can either opt for returning t.Any or any subclass of StorageHashable

        If you return t.Any
        + any arbitrary Folder or FileGroup can be added

        If you return some subclass of StorageHashable
        + You will not be allowed to add any other types

        """
        return t.Any

    @property
    @util.CacheResult
    def items(self) -> util.SmartDict:
        return util.SmartDict(
            allow_nested_dict_or_list=False,
            supplied_items=None,
            use_specific_class=None if self.contains == t.Any else self.contains,
        )

    def init_validate(self):
        # ----------------------------------------------------------- 01
        # folder can have only two fields
        for f in self.dataclass_field_names:
            e.validation.ShouldBeOneOf(
                value=f, values=['file_system', 'for_hashable', 'parent_folder'],
                msgs=[
                    f"Class {self.__class__} can only have limited fields defined "
                    f"in it ... Please refrain from using any new fields ..."
                ]
            ).raise_if_failed()

        # ----------------------------------------------------------- 03
        # call super
        super().init_validate()

    def init(self):
        # call super
        super().init()

        # # Note due to sync that gets called when parent_folder instance
        # # was created the items dict of parent_folder will get instance
        # # of self if already present on disc ... in that case delete the
        # # item in dict and replace with self ...
        # if _hashable.name in self.items.keys():
        #     # Also we do sanity check for integrity to check if hash of
        #     # existing item matches hashable ... this ensure that this is
        #     # safe update of dict
        #     if _hashable.hex_hash != \
        #             self.items[_hashable.name].hex_hash:
        #         raise e.code.NotAllowed(
        #             msgs=[
        #                 f"While syncing from disk the hashable had different "
        #                 f"hex_hash than one assigned now",
        #                 f"We expect that while creating objects of "
        #                 f"StorageHashable it should match with hex_hash of "
        #                 f"equivalent object that was instantiated from disk",
        #                 {
        #                     "yaml_on_dsk":
        #                         self.items[_hashable.name].yaml(),
        #                     "yaml_in_memory":
        #                         _hashable.yaml(),
        #                 }
        #             ]
        #         )
        #     # note we do not call delete() method of item as it will delete
        #     # actual files/folder on disc
        #     # here we just update dict
        #     del self.items[_hashable.name]

        # this is like `get()` for Folder .... note that all
        # FileGroups/Folders will be added here via add_item
        self.sync()

    def create(self) -> Path:
        """
        If there is no Folder we create an empty folder.
        """
        if not self.path.isdir():
            self.path.mkdir()

        # return
        return self.path

    def delete(self, *, force: bool = False):
        """
        Deletes Folder.

        Note: Do not do read_only check here as done in delete_item method as
        it is not applicable here and completely depends on parent folder
        permissions

        Note we delete only empty folders, and the state ... we will not
        support deleting non-empty folders

        note: force kwarg does not matter for a folder but just kept alongside
        FileGroup.delete for generic behaviour

        todo: when `self.contains is None` handle delete differently as we
          will not have items dict
        """
        # todo: do u want to add permission check for
        #  Folder similar to FileGroup
        # when contains is None we delete everything ... this is default
        # behaviour if you want to do something special please override this
        # method
        # todo: fix later
        if self.contains is None:
            # note that this will also delete folder self.path
            util.pathlib_rmtree(path=self.path, recursive=True, force=force)
            # remember to make empty dir as per API ... this will be deleted
            # by delete_post_runner while deleting state files
            self.path.mkdir(exist_ok=True)
        # else since the folder can track items delete them using items and
        # calling the respective delete of items
        else:
            _items = self.items.keys()
            for item in _items:
                # first delete the item physically
                self.items[item].delete(force=force)

        # todo: remove redundant check
        # by now we are confident that folder is empty so just check it
        if not util.io_is_dir_empty(self.path):
            raise e.code.CodingError(
                msgs=[
                    f"The folder should be empty by now ...",
                    f"Check path {self.path}"
                ]
            )

    def warn_about_garbage(self):
        """

        In sync() we skip anything that does not end with *.info this will also
        skip files that are not StorageHashable .... but that is okay for
        multiple reasons ...
         + performance
         + we might want something extra lying around in folders
         + we might have deleted state info but the folders might be
           lying around and might be wise to not delete it
        The max we can do in that case is warn users that some
        thing else is lying around in folder check method
        warn_about_garbage.

        todo: implement this

        """
        ...

    def sync(self):
        """
        Sync is heavy weight call rarely we aim to do all validations here
        and avoid any more validations later ON ...

        todo: We can have special Config class for Folder which can do some
          indexing operation
        """
        # -----------------------------------------------------------------01
        # tracking dict should be empty
        if len(self.items) != 0:
            raise e.code.CodingError(
                msgs=[
                    f"We expect that the tracker dict be empty",
                    f"Make sure that you are calling sync only once i.e. from "
                    f"__post_init__"
                ]
            )

        # -----------------------------------------------------------------02
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
        for f in self.path.glob(pattern=f"*.{Suffix.info}"):

            # construct hashable instance from meta file
            # Note that when instance for hashable is created it will check
            # things on its own periodically
            # Note the __post_init__ call will also sync things if it is folder
            if self.contains == t.Any:
                _cls = m.YamlRepr.get_class(f)
                if _cls is None:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"Cannot process tag at the start ",
                            f"Check: ",
                            f.read_text()
                        ]
                    )
                # noinspection PyTypeChecker
                _hashable = _cls.from_yaml(
                    f, parent_folder=self,
                )  # type: StorageHashable
            else:
                # noinspection PyTypeChecker
                _hashable = self.contains.from_yaml(
                    f, parent_folder=self,
                )  # type: StorageHashable

            # add tuple for tracking
            # todo: no longer needed to add here as when we create instance
            #  the instance adds itself to parent_folder instance ... delete
            #  this code later ... kept for now just for reference
            # noinspection PyTypeChecker
            # self.items[_hashable.name] = _hashable

        # -----------------------------------------------------------------03
        # sync is equivalent to accessing folder
        # so update state manager files
        self.config.append_last_accessed_on()

    def add_item(self, hashable: StorageHashable):

        # since we are adding hashable item that are persisted to disk their
        # state should be present on disk
        if not hashable.is_created:

            # err msg
            if isinstance(hashable, StorageHashable):
                _err_msg = f"This should never happen for " \
                           f"{hashable.__class__} " \
                           f"sub-class, there might be some coding error." \
                           f"Did you forget to call create file/folder " \
                           f"before adding the item."
                raise e.code.CodingError(
                    msgs=[
                        f"We cannot find the state for the following hashable "
                        f"item on disk",
                        hashable.yaml(), _err_msg,
                    ]
                )
            else:
                _err_msg = f"Don't know the type {type(hashable)}"
                raise e.code.ShouldNeverHappen(msgs=[_err_msg])

        # add item
        self.items[hashable.name] = hashable
