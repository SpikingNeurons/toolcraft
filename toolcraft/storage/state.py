"""
Module that will hold code to do state management
"""

import dataclasses
import pathlib
import typing as t
import datetime
import abc

from .. import error as e
from .. import util, settings
from .. import marshalling as m


class Suffix:
    info = ".info"
    config = ".config"


@dataclasses.dataclass
class StateFile(m.YamlRepr, abc.ABC):
    """

    Manages the state of HashableClass
    + save class info in *.info file that has hex value
    + save config info in *.config file ... note that config does not affect
      the *.info file

    todo: We can have the state manager via some decorator like
      storage.StoreField where we create two data frames one for info and other
      for config. Then we can stream them or store to some database where we
      can retrieve them ....
      As of now we limit them to be saved alongside FileGroup, Table and
      Folder ... and hence this class does not make sense here but instead
      should be moved to storage module ....
      But we might have more usage for this so we will retain here

    """
    hashable: m.HashableClass
    # this is the path for which we store state
    # this is the str to which we attach suffix and save it alongside path dir
    path_prefix: str

    @property
    @util.CacheResult
    def path(self) -> pathlib.Path:
        return pathlib.Path(f"{self.path_prefix}{self.suffix}")

    @property
    @abc.abstractmethod
    def suffix(self) -> str:
        ...

    @property
    def is_available(self) -> bool:
        return self.path.exists()

    @property
    @util.CacheResult
    def backup_path(self) -> pathlib.Path:
        e.code.AssertError(
            value1=settings.FileHash.DEBUG_HASHABLE_STATE, value2=True,
            msgs=[
                f"This property can be used only when you have configured "
                f"`config.DEBUG_HASHABLE_STATE=True`"
            ]
        )
        return self.path.parent / f"_backup_{self.path.name}_backup_"

    @abc.abstractmethod
    def sync(self):
        ...

    @abc.abstractmethod
    def reset(self):
        """
        Set to defaults the non mandatory fields
        """
        ...

    def delete(self):
        # todo: remove this later ... once bug is caught that deletes state
        #  files
        # raise Exception(
        #     f"Something is attempting to delete things related to "
        #     f"{self.path} ... keep this until we catch the bug which is "
        #     f"deleting state files"
        # )
        util.io_make_path_editable(self.path)
        self.path.unlink()
        self.reset()

    def backup(self):
        self.backup_path.write_text(self.path.read_text())
        util.io_make_path_read_only(self.backup_path)

    @abc.abstractmethod
    def check_if_backup_matches(self):
        ...

    # noinspection PyTypeChecker
    @classmethod
    def from_dict(
        cls,
        yaml_state: t.Dict[str, "m.SUPPORTED_HASHABLE_OBJECTS_TYPE"],
        **kwargs
    ) -> "StateFile":
        e.code.CodingError(
            msgs=[
                f"For state files we refrain using as_dict and from_dict"
            ]
        )
        raise

    # noinspection PyTypeChecker
    def as_dict(
        self
    ) -> t.Dict[str, "m.SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
        e.code.CodingError(
            msgs=[
                f"For state files we refrain using as_dict and from_dict"
            ]
        )
        raise


@dataclasses.dataclass
class Info(StateFile):
    """
    Info is a tricky class
    + When we serialize it will save it as HashableClass and hence when loaded
      from disk it will still be HashableClass and not the Info class
    """

    @property
    def suffix(self) -> str:
        return Suffix.info

    def sync(self):
        """
        The info on disk if available must match.
        Also note that we only sync hashable and remaining fields are skipped.

        So if you load this yaml using from yaml you will get instance of
        hashableClass and not the Info class
        """
        _yaml = self.hashable.yaml()
        if self.path.exists():
            _yaml_on_disk = self.path.read_text()
            if _yaml_on_disk != _yaml:
                e.code.CodingError(
                    msgs=[
                        "Info file mismatch ... should never happen",
                        "State on disk: ",
                        [_yaml_on_disk],
                        "State in memory: ",
                        [_yaml],
                    ]
                )
        else:
            # handle info file and make it read only
            # ... write hashable info
            self.path.write_text(_yaml)
            # ... make read only as done only once
            util.io_make_path_read_only(self.path)

    def check_if_backup_matches(self):
        if not self.backup_path.exists():
            e.code.CodingError(
                msgs=[
                    f"Looks like you have forgot to backup the state file ..."
                ]
            )

        _self_yaml = self.hashable.yaml()
        _backup_yaml = self.backup_path.read_text()
        if self.hashable.yaml() != self.backup_path.read_text():
            e.code.CodingError(
                msgs=[
                    f"We expect Info state file to be exactly same",
                    dict(
                        _self_yaml=_self_yaml, _backup_yaml=_backup_yaml
                    )
                ]
            )

    def reset(self):
        """
        Set to defaults the non mandatory fields
        """
        ...


class ConfigInternal(m.Internal):
    """
    todo: not possible to get rid of this ... need to see if any optimization
      can be done while setting attributes over config
    """

    start_syncing: bool = False

    def vars_that_can_be_overwritten(self) -> t.List[str]:
        return super().vars_that_can_be_overwritten() + ['start_syncing']


@dataclasses.dataclass
class Config(StateFile):
    """
    todo: update to replace LOCK_ACCESS_FLAG mechanism with internal property
      + move even all below thing sto internal property
        LOCK_ACCESS_FLAG
        BACKUP_YAML_STR_KEY
    """

    class LITERAL(StateFile.LITERAL):
        config_updated_on_list_limit = 10
        accessed_on_list_limit = 10

    # note that created on refers to hashable class of which config is a
    # property ... but we cannot have that field in there as it will affect
    # its unique hex_hash value
    # time when info file was created
    created_on: datetime.datetime = None
    # time when config file was updated ... i.e. when access happened etc
    config_updated_on: t.List[datetime.datetime] = dataclasses.field(
        default_factory=list
    )
    # will be updated when File or Folder is accessed
    accessed_on: t.List[datetime.datetime] = dataclasses.field(
        default_factory=list
    )

    @property
    @util.CacheResult
    def internal(self) -> ConfigInternal:
        return ConfigInternal(owner=self)

    @property
    def suffix(self) -> str:
        return Suffix.config

    @property
    @util.CacheResult
    def dataclass_field_names(self) -> t.List[str]:
        # we do not want to use this values to be saved in serialized state
        return [
            f_name for f_name in super().dataclass_field_names
            if f_name not in ["hashable", "path_prefix"]
        ]

    @property
    def _dict(self) -> t.Dict:
        """
        Refer
        >>> util.notifying_list_dict_class_factory
        """
        _ret = {}
        for _f_name in self.dataclass_field_names:
            _v = getattr(self, _f_name)
            # this handles the proxy list/dict conversions
            if isinstance(_v, list):
                _v = list(_v)
            if isinstance(_v, dict):
                _v = dict(_v)
            _ret[_f_name] = _v
        return _ret

    def __post_init__(self):
        """
        __post_init__ is allowed as it is not m.HashableClass
        """
        # ------------------------------------------------------------ 01
        # if path exists load data dict from it
        # that is sync with contents on disk
        if self.path.exists():
            _dict_from_dick = m.YamlLoader.load(
                cls=dict, file_or_text=self.path
            )
            # update internal dict from HashableDict loaded from disk
            for _k, _v in _dict_from_dick.items():
                # this will take care of conversion of list/dict into
                # notifier list/dict
                # check util.notifying_list_dict_class_factory
                setattr(self, _k, _v)

        # ------------------------------------------------------------ 02
        # start syncing i.e. any updates via __setattr__ will be synced
        # to disc
        self.internal.start_syncing = True

    def __setattr__(self, key, value):
        # for key in dataclass field names then if any of it is list or dict
        # make them special notifier based proxy list and dict
        if key in self.dataclass_field_names:
            if value.__class__ == list:
                # noinspection PyPep8Naming
                NotifierList = \
                    util.notifying_list_dict_class_factory(list, self.sync)
                value = NotifierList(value)
            elif value.__class__ == dict:
                # noinspection PyPep8Naming
                NotifierDict = \
                    util.notifying_list_dict_class_factory(dict, self.sync)
                value = NotifierDict(value)
            else:
                ...

        # call super to set things
        super().__setattr__(key, value)

        # We call sync always as this will occur less frequently compared to
        # __getattribute__
        # Note that list and dict updates will be automatically handled by
        # notifier version
        if self.internal.start_syncing:
            self.sync()

    # noinspection PyMethodOverriding
    def __call__(self) -> "Config":
        # todo: remove this
        raise Exception("NO LONGER SUPPORTED")

    def sync(self):
        # -------------------------------------------------- 01
        # get current state
        _current_state = m.YamlDumper.dump(self._dict)

        # -------------------------------------------------- 02
        # if file exists on the disk then check if the contents are different
        # this helps us catch unexpected syncs
        # if the contents are same then we raise error as nothing is there to
        # update
        if self.path.exists():
            _disk_state = self.path.read_text()
            if _current_state == _disk_state:
                e.code.CodingError(
                    msgs=[
                        f"We expect the state on disk to be different to "
                        f"internal state for config ...",
                        {
                            "_current_state": _current_state,
                            "_disk_state": _disk_state
                        },
                        f"This looks like unexpected sync as nothing has "
                        f"changed in config"
                    ]
                )

        # -------------------------------------------------- 03
        # write to disk
        self.path.write_text(_current_state)

    def reset(self):
        """
        Set to defaults the non mandatory fields
        """
        # first we need to stop syncing as we will reset the fields
        self.internal.start_syncing = False

        # Set non mandatory fields to default values.
        # Note that list self.dataclass_field_names already skips mandatory
        # fields
        for f_name in self.dataclass_field_names:
            # noinspection PyUnresolvedReferences
            f = self.__dataclass_fields__[f_name]
            v = f.default
            if v == dataclasses.MISSING:
                v = f.default_factory()
            if v == dataclasses.MISSING:
                e.code.CodingError(
                    msgs=[
                        f"Field {f_name} does not have any default value to "
                        f"extract",
                        f"We assume it is non mandatory field and hence we "
                        f"expect a default to be provided"
                    ]
                )
            setattr(self, f_name, v)

        # set back to sync so that any further updates can be synced
        self.internal.start_syncing = True

    # noinspection DuplicatedCode
    def append_last_accessed_on(self):
        # this can never happen
        if len(self.accessed_on) > \
                self.LITERAL.accessed_on_list_limit:
            e.code.CodingError(
                msgs=[
                    f"This should never happens ... did you try to append "
                    f"last_accessed_on list multiple times"
                ]
            )
        # limit the list
        if len(self.accessed_on) == \
                self.LITERAL.accessed_on_list_limit:
            self.accessed_on = self.accessed_on[1:]
        # append time
        self.accessed_on.append(datetime.datetime.now())

    def check_if_backup_matches(self):
        # noinspection DuplicatedCode
        if not self.backup_path.exists():
            e.code.CodingError(
                msgs=[
                    f"Looks like you have forgot to backup the state file ..."
                ]
            )

        # get the state as dict
        _self_yaml_dict = self.as_dict()
        _backup_yaml_dict = self.from_yaml(
            self.backup_path.read_text()
        ).as_dict()

        # match lengths
        if len(_self_yaml_dict) != len(_backup_yaml_dict):
            e.code.CodingError(
                msgs=[
                    f"The config does not have same number of keys as that "
                    f"in backup"
                ]
            )

        # keys that must differ
        _keys_that_must_differ = ['created_on']

        # keys that must not differ
        _keys_that_must_not_differ = ['auto_hashes']

        # loop over keys
        for k in _self_yaml_dict.keys():
            _matches = _self_yaml_dict[k] == _backup_yaml_dict[k]
            if k in _keys_that_must_differ:
                if _matches:
                    e.code.CodingError(
                        msgs=[
                            f"We expect value for key `{k}` to differ in "
                            f"backup",
                            f"Found value: {_backup_yaml_dict[k]}"
                        ]
                    )
            if k in _keys_that_must_not_differ:
                if not _matches:
                    e.code.CodingError(
                        msgs=[
                            f"We expect value for key `{k}` to not differ in "
                            f"backup",
                            dict(
                                _self=_self_yaml_dict[k],
                                _backup=_backup_yaml_dict[k],
                            )
                        ]
                    )
