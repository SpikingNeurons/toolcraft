from base64 import decodebytes

import paramiko
import pysftp


keydata = b"""host_key"""

# noinspection PyTypeChecker
key = paramiko.RSAKey(data=decodebytes(keydata))

cnopts = pysftp.CnOpts()

cnopts.hostkeys.add("host", "ssh-rsa 2048", key)

with pysftp.Connection("host", username="", password="", cnopts=cnopts) as sftp:
    sftp.mkdir("win_scp_upl")
    with sftp.cd("win_scp_upl"):
        sftp.put("hello_world.graphql")
