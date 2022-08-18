"""
Holds the base classes for storage module.
These are special hashables whose state can be serialized on disk.
"""

import typing as t
import pathlib
import datetime
import dataclasses
import abc
_now = datetime.datetime.now

from .. import util, logger, settings
from .. import marshalling as m
from .. import error as e
from .. import richy
from . import file_system as _fs

# noinspection PyUnreachableCode
if False:
    from . import state, folder

_LOGGER = logger.get_logger()

_DOT_DOT_TYPE = t.Literal['..']
# noinspection PyUnresolvedReferences
_DOT_DOT = _DOT_DOT_TYPE.__args__[0]


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=[
        'config', 'info', 'path', 'uses_parent_folder', 'uses_file_system', ],
    things_not_to_be_overridden=[
        'path', 'uses_parent_folder', 'uses_file_system', ]
)
class StorageHashable(m.HashableClass, abc.ABC):

    # Either provide one of below in child classes ...
    #   this is just provided here for reference
    # file_system: str
    # parent_folder: "folder.Folder"

    @property
    @util.CacheResult
    def config(self) -> "state.Config":
        from . import state
        return state.Config(hashable=self)

    @property
    @util.CacheResult
    def info(self) -> "state.Info":
        from . import state
        return state.Info(hashable=self)

    @property
    @util.CacheResult
    def path(self) -> _fs.Path:
        """
        Never override this.
        Always resolve folder structure from group_by and name.
        """
        # ------------------------------------------------------------- 01
        # get group for split strs that dictates grouping
        _split_strs = self.group_by

        # ------------------------------------------------------------- 02
        # get path from parent_folder if uses_parent_folder
        if self.uses_parent_folder:
            _path = self.parent_folder.path
        # else it will be file system so get from it
        else:
            _path = _fs.Path.get_root(fs_name=self.file_system)

        # ------------------------------------------------------------- 03
        # note that we allow separators in name so split name with seperator
        _split_strs += self.name.split(_path.sep)
        # build path
        for _ in _split_strs:
            _path /= _

        # return
        return _path

    @property
    @util.CacheResult
    def uses_file_system(self) -> bool:
        _found_file_system = "file_system" in self.dataclass_field_names
        if not _found_file_system:
            _found_file_system = "file_system" in dir(self)
            if _found_file_system:
                if not isinstance(getattr(self.__class__, "file_system"), property):
                    raise e.code.CodingError(
                        msgs=[
                            f"Was expecting `file_system` to be property in class "
                            f"{self.__class__}"
                        ]
                    )
        return _found_file_system

    @property
    @util.CacheResult
    def uses_parent_folder(self) -> bool:
        _found_parent_folder = "parent_folder" in self.dataclass_field_names
        if not _found_parent_folder:
            _found_parent_folder = "parent_folder" in dir(self)
            if _found_parent_folder:
                if not isinstance(getattr(self.__class__, "parent_folder"), property):
                    raise e.code.CodingError(
                        msgs=[
                            f"Was expecting `parent_folder` to be property in class "
                            f"{self.__class__}"
                        ]
                    )
        return _found_parent_folder

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
            method=cls.create,
            pre_method=cls.create_pre_runner,
            post_method=cls.create_post_runner,
        )

        # hook up delete
        util.HookUp(
            cls=cls,
            method=cls.delete,
            pre_method=cls.delete_pre_runner,
            post_method=cls.delete_post_runner,
        )

    def init_validate(self):
        from .folder import Folder

        # ----------------------------------------------------------- 01
        # test for field/property file_system or parent_folder
        # calling property does the check
        _uses_parent_folder = self.uses_parent_folder
        _uses_file_system = self.uses_file_system
        if not(_uses_parent_folder ^ _uses_file_system):
            raise e.code.CodingError(
                msgs=[
                    f"Either supply dataclass-field/property "
                    f"`file_system` or `parent_folder` "
                    f"for class {self.__class__} ...",
                    "We will raise error if both or none is specified ...",
                    dict(_uses_file_system=_uses_file_system,
                         _uses_parent_folder=_uses_parent_folder)
                ]
            )

        # ----------------------------------------------------------- 02
        # if _uses_parent_folder test instance as we do not have control over
        # type checking ... as every class has fresh definition for it
        if _uses_parent_folder:
            # ------------------------------------------------------- 02.01
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
            if self.parent_folder == _DOT_DOT:
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

            # ------------------------------------------------------- 02.02
            # should be instance of Folder
            e.validation.ShouldBeInstanceOf(
                value=self.parent_folder, value_types=(Folder,),
                msgs=[
                    "Please supply correct value for dataclass field `parent_folder`"
                ]
            ).raise_if_failed()

        # ----------------------------------------------------------- 03
        # if not _uses_parent_folder then test if valid file_system
        else:
            e.validation.ShouldBeOneOf(
                value=self.file_system, values=_fs.available_file_systems(),
                msgs=[
                    "Expecting file_system to be valid ..."
                ]
            ).raise_if_failed()

        # ----------------------------------------------------------- 04
        # if path exists check if it is a folder
        if self.path.exists():
            if not self.path.isdir():
                raise e.validation.NotAllowed(
                    msgs=[
                        f"We expect {self.path} to be a dir"
                    ]
                )

        # ----------------------------------------------------------- 05
        # call super
        super().init_validate()

    @classmethod
    def from_dict(
        cls, yaml_state: t.Dict[str, "m.SUPPORTED_HASHABLE_OBJECTS_TYPE"], **kwargs
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

    def create(self) -> t.Union[_fs.Path, t.List[_fs.Path]]:
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
        self, *, hooked_method_return_value: t.Union[_fs.Path, t.List[_fs.Path]]
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
        self.config.created_on = _now()

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
    def delete_pre_runner(self, *, force: bool):
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
        self, *, hooked_method_return_value: t.Any, force: bool
    ):
        # delete state files as they were created along with the
        # files for this StorageHashable in create_post_runner
        self.info.delete()
        self.config.delete()

        # also delete the empty path folder
        try:
            self.path.rmdir()
        except OSError as _ose:
            raise e.code.CodingError(
                msgs=[
                    f"All the files inside folder should be deleted by now ...",
                    f"Expected path dir to be empty",
                    f"Check path {self.path}",
                    _ose
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
