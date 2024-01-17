from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GoogleDriveVars:
    GAUTH = GoogleAuth()
    GAUTH.LocalWebserverAuth()
    DRIVE = GoogleDrive(GAUTH)
    FOLDERS_NAME_TO_ID = dict()
