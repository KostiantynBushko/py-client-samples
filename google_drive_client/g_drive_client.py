#!/usr/bin/python3

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.auth import ServiceAccountCredentials
import sys
import os


class GoogleDriveClient:
    def __init__(self, cred_json_file):
        """
        Create Google Drive client using service configuration json
        :param cred_json_file:
        """
        auth = GoogleAuth()
        auth.credentials = ServiceAccountCredentials.from_json_keyfile_name(cred_json_file,
                                                                            ['https://www.googleapis.com/auth/drive'])
        self.drive = GoogleDrive(auth)

    def mkdir(self, drive_dir_path):
        """
        Create folders on drive recursively
        :param drive_dir_path: absolute path to folder i.e. 'my_folder/new_folder'
        :return: an object of newly created folder on drive
        """
        list_dirs = str(drive_dir_path).split('/')
        current_dir_obj = None
        for d in list_dirs:
            if d == '':
                continue
            dir_obj = self.find_dir(d)
            if dir_obj:
                if current_dir_obj:
                    dir_obj['parents'] = [{u'id': current_dir_obj['id']}]
                current_dir_obj = dir_obj
                current_dir_obj.Upload()
                print('current folder id: {} title: {}'.format(current_dir_obj['id'], current_dir_obj['title']))
                continue
            folder = self.drive.CreateFile({'title': '{}'.format(d), 'mimeType': 'application/vnd.google-apps.folder'})
            if current_dir_obj:
                folder['parents'] = [{u'id': current_dir_obj['id']}]
            folder.Upload()
            current_dir_obj = folder
        return current_dir_obj

    def list(self, drive_dir_obj):
        dir_list = self.drive.ListFile({'q': "'{}' in parents and trashed=false".format(drive_dir_obj)}).GetList()
        return dir_list

    def find_dir(self, dir_path=None):
        list_dirs = str(dir_path).split('/')
        current_drive_folder = None
        for d in list_dirs:
            query = "title='{}' and mimeType contains 'application/vnd.google-apps.folder' and trashed=false"\
                .format(d)
            dir_list = self.drive.ListFile({'q': query}).GetList()
            print('list: {}'.format(dir_list))
            if dir_list.__len__() == 0:
                return None
            else:
                current_drive_folder = dir_list[0]
        return current_drive_folder

    def upload_file(self, drive_path, drive_file_name, host_file_path):
        """
        :param drive_path: absolute path on google drive
        :param drive_file_name: name of the file on google drive
        :param host_file_path: an absolute path to file in the host machine file system
        :return: an file-object which describes file on google drive
        """
        dir_obj = self.find_dir(dir_path=drive_path)

        if dir_obj is None:
            dir_obj = self.mkdir(drive_path)

        list_files_obj = self.list(dir_obj['id'])
        file_obj = None

        for f_obj in list_files_obj:
            if f_obj['title'] == drive_file_name:
                file_obj = f_obj
                break
        if file_obj is None:
            file_obj = self.drive.CreateFile({'title': drive_file_name, 'parents': [{u'id': dir_obj['id']}]})

        file_obj.SetContentFile(host_file_path)
        file_obj.Upload()
        print(file_obj['title'])
        return file_obj


if __name__ == '__main__':
    google_drive_path = None
    host_file_path = None
    google_service_cred = None

    def cmd_help():
        print('Usage: <abs path on google drive> <abs path on host> <abs path to service credentials file>')

    if len(sys.argv) < 3:
        cmd_help()
        exit(1)

    google_drive_path = sys.argv[1]
    host_file_path = sys.argv[2]
    google_service_cred = sys.argv[3]

    print('G DRIVE PATH: {}'.format(google_drive_path))
    print('HOST FS PATH: {}'.format(host_file_path))
    print('SERVICE CREDENTIALS PATH: {}'.format(google_service_cred))

    client = GoogleDriveClient(google_service_cred)
    status = client.upload_file(drive_path=google_drive_path, drive_file_name=os.path.basename(host_file_path),
                                host_file_path=host_file_path)
    print('Upload status: {}'.format(status))

    exit(0)