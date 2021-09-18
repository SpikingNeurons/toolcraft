import pathlib
import typer
import yaml

from . import Tool
from .. import error as e
from .. import logger
from .. import util

_LOGGER = logger.get_logger()


class SftpTool(Tool):

    @classmethod
    def command_fn(
        cls,
        file_name: str = typer.Option(
            ...,
            help="The yaml file that contains details of sftp server and "
                 "download file details.",
        )
    ):
        # ------------------------------------------------------- 01
        # read details from input yaml file
        yaml_file = pathlib.Path(file_name)
        if not yaml_file.exists():
            e.validation.NotAllowed(
                msgs=[
                    f"We cannot find file `{file_name}`"
                ]
            )
        yaml_str = yaml_file.read_text()
        files_to_download = yaml.safe_load(yaml_str)['files']
        sftp_details = yaml.safe_load(yaml_str)['sftp']

        # ------------------------------------------------------- 02
        # the download dir to store files
        # todo: need to directly download to sftp server ... is that possible ??
        downloads_dir = yaml_file.parent / "downloads"
        if not downloads_dir.exists():
            downloads_dir.mkdir()

        # ------------------------------------------------------- 03
        # iterate over files to download and check hash
        _LOGGER.info(
            msg="Downloading and uploading files to SFTP server at:",
            msgs=[
                sftp_details
            ]
        )
        for file_to_download in files_to_download:
            # create folder and file path
            _file_folder = downloads_dir / file_to_download['folder']
            if not _file_folder.exists():
                _file_folder.mkdir()
            _file_path = _file_folder / file_to_download['file']

            # if file exists ... just check hash
            if _file_path.exists():
                util.check_hash_sha256(_file_path, file_to_download['hash'])
                continue

            # if file on server ... bypass
            # todo: test if file on server ... so that we can bypass
            _file_on_server = False
            if _file_on_server:
                continue

            # download file
            util.download_file(_file_path, file_to_download['url'])

            # check hash
            util.check_hash_sha256(_file_path, file_to_download['hash'])

            # upload file to sftp
            # todo: add method to util.py to upload file using sftp_details

            # delete local files to save disk space
            # todo: uncomment this to delete locally downloaded file to save
            #  disk space
            # _file_path.unlink()
