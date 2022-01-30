"""
Holds the base classes for storage module.
These are special hashables whose state can be serialized on disk.
"""

import typing as t
import pathlib
import datetime
import dataclasses
import abc

from .. import util, logger, settings
from .. import marshalling as m
from .. import error as e
from . import state

# noinspection PyUnreachableCode
if False:
    from . import store

_LOGGER = logger.get_logger()

_DOT_DOT_TYPE = t.Literal['..']
# noinspection PyUnresolvedReferences
_DOT_DOT = _DOT_DOT_TYPE.__args__[0]


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['config', 'info', 'path', 'root_dir'],
    things_not_to_be_overridden=['path']
)
class StorageHashable(m.HashableClass, abc.ABC):

    @property
    @util.CacheResult
    def config(self) -> state.Config:
        return state.Config(
            hashable=self,
            path_prefix=self.path.as_posix(),
        )

    @property
    @util.CacheResult
    def info(self) -> state.Info:
        return state.Info(
            hashable=self,
            path_prefix=self.path.as_posix(),
        )

    @property
    @util.CacheResult
    def internal(self) -> m.Internal:
        return m.Internal(self)

    @property
    @util.CacheResult
    def path(self) -> pathlib.Path:
        """
        Never override this.
        Always resolve folder structure from group_by and name.
        Note that root_dir can still be overridden if you want different
        result locations
        """
        if isinstance(self.group_by, list):
            _split_strs = self.group_by
        elif isinstance(self.group_by, str):
            _split_strs = [self.group_by]
        elif self.group_by is None:
            _split_strs = []
        else:
            raise e.code.ShouldNeverHappen(
                msgs=[
                    f"unsupported group_by value {self.group_by}"
                ]
            )
            raise
        _path = self.root_dir
        for _ in _split_strs:
            _path /= _
        return _path / self.name

    @property
    @util.CacheResult
    def root_dir(self) -> pathlib.Path:
        from .folder import Folder

        # if not using parent_folder then this property should never be
        # called as it will ideally overridden
        if not self.uses_parent_folder:
            raise e.code.ShouldNeverHappen(
                msgs=[
                    f"You have configured class {self.__class__} to not to use "
                    f"parent_folder so we expect you to override `root_dir` "
                    f"property inside class {self.__class__}"
                ]
            )

        # get parent folder
        try:
            _parent_folder = getattr(self, 'parent_folder')
        except AttributeError:
            raise e.code.CodingError(
                msgs=[
                    f"This is already checked .... ideally field "
                    f"parent_folder should be present in class {self.__class__}"
                ]
            )
            raise

        # If parent_folder is provided this property will not be overridden,
        # hence we will reach here.
        # In order to avoid creating Folder instance for parent_folder we use
        # `..` string while saving to disc. This makes sure that there is no
        # recursive instances of Folder being created. These instances again
        # tries to sync leading to recursion
        # But that means the Folder which is creating this instance must set
        # itself as parent_folder.
        # Also check documentation for `Folder.sync()` and
        # `StorageHashable.init_validate()`
        # Note in init_validate if self.parent_folder is `..` we raise error
        # stating that you are creating instance from yaml file directly and
        # it is not allowed as parent_folder should do it while syncing
        if _parent_folder == _DOT_DOT:
            raise e.code.CodingError(
                msgs=[
                    f"Yaml on disk can have `..` string so the Folder which "
                    f"is creating this instance must update it and then call "
                    f"__post_init__ over the StorageHashable",
                    f"{Folder.sync} is responsible to set parent_folder while "
                    f"syncing.",
                    f"While in case if you are creating instance "
                    f"directly from yaml file then "
                    f"{StorageHashable.init_validate} should ideally block "
                    f"you as it is not possible to create instance.",
                    f"Also note that we do all this because hex_hash will be "
                    f"corrupt if parent_folder is not set appropriately "
                    f"before `Hashable.init` runs"
                ]
            )
            raise

        # Now if parent_folder is Folder simply return the path of
        # parent_folder as it is the root plus the name for this StorageHashable
        if isinstance(_parent_folder, Folder):
            return _parent_folder.path

        # if above thing does not return that means we have a problem so
        # raise error
        raise e.code.CodingError(
            msgs=[
                f"The field parent_folder is not None nor it is valid "
                f"Folder",
                f"The type is {type(_parent_folder)}"
            ]
        )
        raise

    @property
    def group_by(self) -> t.Optional[t.Union[str, t.List[str]]]:
        """
        Default is use not grouping ... override this if you need grouping
        """
        return None

    @property
    def uses_parent_folder(self) -> bool:
        """
        Adds a parent_folder behavior i.e. this subclass of StorageHashable
        can be managed by parent_folder
        """
        return False

    @property
    def is_created(self) -> bool:
        _info_there = self.info.is_available
        _config_there = self.config.is_available
        if _info_there ^ _config_there:
            raise e.code.CodingError(
                msgs=[
                    f"Both config and info should be present or none should "
                    f"be present ...",
                    dict(
                        _info_there=_info_there, _config_there=_config_there
                    )
                ]
            )
        return _info_there and _config_there

    @classmethod
    def hook_up_methods(cls):
        # call super
        super().hook_up_methods()

        # hook up create
        util.HookUp(
            cls=cls,
            silent=True,
            method=cls.create,
            pre_method=cls.create_pre_runner,
            post_method=cls.create_post_runner,
        )

        # hook up delete
        util.HookUp(
            cls=cls,
            silent=True,
            method=cls.delete,
            pre_method=cls.delete_pre_runner,
            post_method=cls.delete_post_runner,
        )

    def init_validate(self):
        from .folder import Folder

        # ----------------------------------------------------------- 01
        # if uses_parent_folder
        if self.uses_parent_folder:
            # ------------------------------------------------------- 01.01
            # check if necessary field added
            if 'parent_folder' not in self.dataclass_field_names:
                raise e.code.CodingError(
                    msgs=[
                        f"We expect you to define field `parent_folder` as you "
                        f"have configured property `uses_parent_folder` to "
                        f"True for class {self.__class__}"
                    ]
                )
            # ------------------------------------------------------- 01.02
            # the root_dir property must not be overrided
            if self.__class__.root_dir != StorageHashable.root_dir:
                raise e.code.CodingError(
                    msgs=[
                        f"Please do not override property `root_dir` in class "
                        f"{self.__class__} as it is configured to use "
                        f"parent_folder"
                    ]
                )
            # ------------------------------------------------------- 01.03
            # test if parent_folder is Folder
            _parent_folder = getattr(self, 'parent_folder')
            if not isinstance(_parent_folder, Folder):
                if _parent_folder != _DOT_DOT:
                    raise e.code.CodingError(
                        msgs=[
                            f"We expect parent_folder to be set with instance "
                            f"of type {Folder}",
                            f"Instead found value of type "
                            f"{type(_parent_folder)}"
                        ]
                    )
            # ------------------------------------------------------- 01.04
            # If parent_folder is provided this property will not be overridden,
            # hence we will reach here.
            # In order to avoid creating Folder instance for parent_folder
            # we use `..` string while saving to disc. This makes sure that
            # there is no recursive instances of Folder being created. These
            # instances again tries to sync leading to recursion
            # But that means the Folder which is creating this instance must set
            # itself as parent_folder.
            # Also check documentation for `Folder.sync()` and
            # `StorageHashable.init_validate()`
            # Note in init_validate if self.parent_folder is `..` we raise error
            # stating that you are creating instance from yaml file directly and
            # it is not allowed as parent_folder should do it while syncing
            if _parent_folder == _DOT_DOT:
                raise e.code.CodingError(
                    msgs=[
                        f"Problem with initializing {self.__class__}",
                        f"Yaml on disc can have `..` string so the Folder "
                        f"which is creating this instance must update it and "
                        f"then call __post_init__ over the StorageHashable",
                        f"{Folder.sync} is responsible to set parent_folder "
                        f"while syncing.",
                        f"While in case if you are creating instance "
                        f"directly from yaml file then we block "
                        f"you as it is not possible to create instance.",
                        f"Also note that we do all this because hex_hash "
                        f"will be corrupt if parent_folder is not set "
                        f"appropriately before `Hashable.init` runs"
                    ]
                )
                raise
            # ------------------------------------------------------- 01.05
            # if parent_folder supplied check what it can contain
            _contains = _parent_folder.contains
            # if None
            if _contains != t.Any:
                # note we do not use isinstance() as all folder
                # subclasses will be concrete and subclassing is not anything
                # special as there is no hierarchy in folder types
                if self.__class__ != _parent_folder.contains:
                    raise e.code.NotAllowed(
                        msgs=[
                            f"The parent_folder is configured to contain only "
                            f"instances of class "
                            f"{_parent_folder.contains} but you "
                            f"are trying to add instance of type "
                            f"{self.__class__}"
                        ]
                    )

        # ----------------------------------------------------------- 02
        # check for path length
        e.io.LongPath(path=self.path, msgs=[])
        # if path exists check if it is a folder
        if self.path.exists():
            if not self.path.is_dir():
                raise e.validation.NotAllowed(
                    msgs=[
                        f"We expect {self.path} to be a dir"
                    ]
                )

        # ----------------------------------------------------------- 03
        # call super
        super().init_validate()

    def init(self):
        # ----------------------------------------------------------- 01
        # call super
        super().init()

        # ----------------------------------------------------------- 02
        # if root dir does not exist make it
        if not self.path.exists():
            self.path.mkdir(parents=True)

        # ----------------------------------------------------------- 03
        # if not created create
        if not self.is_created:
            self.create()

        # ----------------------------------------------------------- 04
        # if parent_folder can track then add self to items
        # Note that when contains is None we might still have Folder and
        # FileGroup inside it but we will not do tracking for it and it is
        # job of user to handle in respective parent_folder class
        if self.uses_parent_folder:
            # noinspection PyUnresolvedReferences
            _parent_folder = self.parent_folder  # type: Folder
            if _parent_folder.contains is not None:
                # add item ...
                # Note that item can already exist due to sync in that case
                _parent_folder.add_item(hashable=self)

    @classmethod
    def from_dict(
        cls,
        yaml_state: t.Dict[str, "m.SUPPORTED_HASHABLE_OBJECTS_TYPE"],
        **kwargs
    ) -> "StorageHashable":
        if "parent_folder" in yaml_state.keys():
            # update .. to parent_folder supplied from kwargs
            if yaml_state["parent_folder"] == _DOT_DOT:
                if "parent_folder" not in kwargs.keys():
                    raise e.code.CodingError(
                        msgs=[
                            f"The yaml_state dict loaded from file_or_text "
                            f"does has parent_folder set to `..`",
                            f"This means we do not have access to "
                            f"parent_folder instance so please supply it "
                            f"while Folder syncs files/folders inside it.",
                            f"Note that if you are using from_yaml then also "
                            f"you can supply the extra kwarg so that "
                            f"from_dict receives it."
                        ]
                    )
                else:
                    yaml_state["parent_folder"] = kwargs["parent_folder"]

        # noinspection PyArgumentList
        return cls(**yaml_state)

    def as_dict(
        self
    ) -> t.Dict[str, m.SUPPORTED_HASHABLE_OBJECTS_TYPE]:
        # get dict from super
        _dict = super().as_dict()

        # if uses parent_folder
        if self.uses_parent_folder:
            # get parent folder
            _parent_folder = getattr(self, 'parent_folder')

            # if there is parent_folder update it to ..
            if _parent_folder == _DOT_DOT:
                raise e.code.CodingError(
                    msgs=[
                        f"If loading from yaml on disk make sure that a "
                        f"Folder is doing that un sync so that parent_folder "
                        f"is set appropriately before calling __post_init__ on "
                        f"StorageHashable"
                    ]
                )

            # modify dict so that representation is change on disc
            # note that this does not modify self.__dict__ ;)
            # we do this only when parent_folder is available
            _dict['parent_folder'] = _DOT_DOT

        # return
        return _dict

    def create_pre_runner(self):
        # check if already created
        if self.is_created:
            raise e.code.NotAllowed(
                msgs=[
                    f"Things related to hashable class {self.__class__} "
                    f"with name `{self.name}` has already been created ...",
                ]
            )

    def create(self) -> t.Any:
        raise e.code.CodingError(
            msgs=[
                f"There is nothing to create for class {self.__class__}",
                F"You might need to override this method if you have "
                F"something to create ...",
                f"If you override this method make sure you override "
                f"corresponding `delete()` too ..."
            ]
        )

    # noinspection PyUnusedLocal
    def create_post_runner(
        self, *, hooked_method_return_value: t.Any
    ):

        # ----------------------------------------------------------- 01
        # The below call will create state manager files on the disk
        # check if .info and .config file exists i.e. state exists
        if self.config.is_available:
            raise e.code.CodingError(
                msgs=[
                    f"Looks like you have updated config before this parent "
                    f"create_post_runner was called.",
                    f"Try to make updates to config after the config is "
                    f"created the parent create_post_runner by calling sync()"
                ]
            )
        if self.info.is_available:
            raise e.code.CodingError(
                msgs=[
                    f"looks like info file for this StorageHashable is "
                    f"already present",
                    f"As files were just created we expect that this state "
                    f"file should not be present ..."
                ]
            )
        # redundant
        _ = self.is_created

        # ----------------------------------------------------------- 02
        # sync to disk ... note that from here on state files will be on the
        # disc and the child methods that will call super can take over and
        # modify state files like config
        self.info.sync()
        self.config.sync()

        # ----------------------------------------------------------- 03
        # also sync the created on ... note that config can auto sync on
        # update to its fields
        self.config.created_on = datetime.datetime.now()

        # ----------------------------------------------------------- 04
        # check if property updated
        if not self.is_created:
            raise e.code.NotAllowed(
                msgs=[
                    f"Did you forget to update appropriately the things in "
                    f"`create()` method of {self.__class__}",
                    f"Property `self.is_created` should return `True` as "
                    f"things are now created."
                ]
            )

    # noinspection PyUnusedLocal
    def delete_pre_runner(self, *, force: bool = False):
        # check if already created
        if not self.is_created:
            raise e.code.NotAllowed(
                msgs=[
                    f"Things related to hashable class {self.__class__} are "
                    f"not created ..."
                ]
            )

    def delete(self, *, force: bool = False) -> t.Any:
        raise e.code.CodingError(
            msgs=[
                f"There is nothing to delete for class {self.__class__}",
                F"You might need to override this method if you have "
                F"something to delete ...",
                f"You only `delete()` if you create something in `create()`"
            ]
        )

    # noinspection PyUnusedLocal
    def delete_post_runner(
        self, *, hooked_method_return_value: t.Any
    ):
        # delete state files as they were created along with the
        # files for this StorageHashable in create_post_runner
        self.info.delete()
        self.config.delete()

        # also delete the empty path folder
        if util.io_is_dir_empty(self.path):
            self.path.rmdir()
        else:
            raise e.code.CodingError(
                msgs=[
                    f"All the files inside folder should be deleted by now ...",
                    f"Expected path dir to be empty",
                    f"Check path {self.path}"
                ]
            )

        # check if property updated
        if self.is_created:
            raise e.code.NotAllowed(
                msgs=[
                    f"Did you forget to update appropriately the things in "
                    f"`delete()` method of {self.__class__}",
                    f"Property `self.is_created` should return `False` as "
                    f"things are now deleted."
                ]
            )

        # if parent_folder is there try to remove item from the tracking dict
        # items
        if self.uses_parent_folder:
            # get parent folder
            _parent_folder = getattr(self, 'parent_folder')
            # if parent folder can track then delete items that it has tracked
            if _parent_folder.contains is not None:
                # just do sanity check if we are having same item
                if id(self) != id(_parent_folder.items[self.name]):
                    raise e.code.CodingError(
                        msgs=[
                            f"We expect these objects to be same ... "
                            f"make sure to add item using "
                            f"parent_folder.add_item() method for integrity"
                        ]
                    )
                # in init() we added self by calling
                # self.parent_folder.add_item(self) ... now we just remove the
                # item from tracking dict items so that parent folder is in sync
                del _parent_folder.items[self.name]

        # now we have removed strong reference to self in parent_folder.items
        # dict ... let us make this instance useless as files are deleted
        # hence we want to make sure any other references will fail to use
        # this instance ...
        # To achieve this we just clear out the internal __dict__
        if not settings.FileHash.DEBUG_HASHABLE_STATE:
            self.__dict__.clear()
