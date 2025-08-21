
from ftplib import FTP_TLS, error_perm
from os.path import join as pjoin
import os
import typing


class FTPDataExchange:
    """
    A class for managing file transfers and operations on Box using FTPS.

    For more information:
    - Box FTPS documentation: https://support.box.com/hc/en-us/articles/360044194853-I-m-Having-Trouble-Using-FTP-with-Box
    - ftplib documentation: https://docs.python.org/3/library/ftplib.html

    Attributes:
        host (str): The FTPS host for the Box account.
        user (str): The FTPS username for authentication.
        password (str): The FTPS password for authentication.
        ftp (ftplib.FTP_TLS): The FTPS connection object.

    Methods:
        __init__(self, ftp_host: str, ftp_user: str, ftp_passwd: str):
            Initialize a BoxDataManager instance and connect to Box via FTPS.

        connect_to_remote(self):
            Connect to Box via FTPS using the provided credentials.

        list_files_remote(self, remote_directory: str = '/') -> list:
            List files in the specified remote directory on Box via FTPS.

        walk_remote_tree(self, remote_root_directory: str) -> typing.Generator:
            Traverse the remote directory tree using breadth-first search and yield each directory path.

        recursively_copy_files_from_remote_directory(self, local_root_directory: str, remote_root_directory: str,
                                                     overwrite_local_file: bool = False, verbose: bool = False,
                                                     dry_run: bool = False, filetype_restrictions: list = []) -> None:
            Recursively copy files from a remote directory to a local directory using FTPS.

        walk_local_tree(self, local_root_directory: str):
            Traverse the local directory tree using breadth-first search and yield each directory path.

        recursively_copy_files_from_local_directory(self, remote_root_directory: str, local_root_directory: str,
                                                    overwrite_remote_file: bool = False, verbose: bool = False,
                                                    dry_run: bool = False, filetype_restrictions: list = []) -> None:
            Recursively copy files from a local directory to a remote directory using FTPS.

        copy_file_to_remote_directory(self, local_file_path: str, target_remote_directory: str) -> None:
            Copy a file from local directory to a remote directory using FTPS.
    """

    def __init__(self, ftp_host: str, ftp_user: str, ftp_passwd: str):
        """
        Initialize a BoxDataManager instance and connect to Box via FTPS.

        Parameters:
            ftp_host (str): The FTPS host for the Box account.
            ftp_user (str): The FTPS username for authentication.
            ftp_passwd (str): The FTPS password for authentication.
        """

        self.host = ftp_host
        self.user = ftp_user
        self.password = ftp_passwd
        self.connect_to_remote()

    def connect_to_remote(self):
        """
        Connect to Box via FTPS using the provided credentials.

        Raises:
            Exception: If the connection to Box via FTPS fails.
        """
        try:
            self.ftp = FTP_TLS(self.host)  # Use FTP_TLS for FTPS connection
            self.ftp.login(user=self.user, passwd=self.password)

            # If you want explicit FTPS, you would call self.ftp.prot_p()
            self.ftp.prot_p()  # Switch to secure data connection
            self.ftp.set_pasv(True)

        except Exception as error:
            raise Exception(error)

    def list_files_remote(self, remote_directory: str = '/') -> list:
        """
        List files in the specified remote directory on Box via FTPS.

        Parameters:
            remote_directory (str, optional): The remote directory to list files from. Default is '/'.

        Returns:
            list: A list of file names in the specified remote directory.

        Raises:
            Exception: If listing files in the remote directory fails.
        """
        try:
            self.ftp.cwd(remote_directory)
            file_list = []
            self.ftp.retrlines('LIST', lambda x: file_list.append(x.split()[-1]))
            return file_list

        except Exception as error:
            raise Exception(error)

    def walk_remote_tree(self, remote_root_directory: str) -> typing.Generator:
        """
        Traverse the remote directory tree using breadth-first search and yield each directory path.

        Parameters:
            remote_root_directory (str, optional): The root directory on the remote FTPS server.

        Yields:
            str: The path of each directory in the remote tree.
        """
        yield remote_root_directory

        queue = [remote_root_directory]

        while queue:
            current_directory = queue.pop(0)
            self.ftp.cwd(current_directory)

            filelist = [i for i in self.ftp.mlsd()]

            for f in filelist:
                if f[0].startswith('.'):
                    continue
                if f[1]['type'] == 'dir':
                    directory_in_tree = pjoin(current_directory, f[0])
                    queue.append(directory_in_tree)
                    yield directory_in_tree

    def recursively_copy_files_from_remote_directory(self, local_root_directory: str, remote_root_directory: str,
                                                     overwrite_local_file: bool = False, verbose: bool = False,
                                                     dry_run: bool = False, filetype_restrictions: list = []) -> None:
        """
        Recursively copy files from a remote directory to a local directory using FTPS.

        Parameters:
            local_root_directory (str): The root directory for local copies. Will be created if it does not exist.
            remote_root_directory (str): The root directory on the remote FTPS server.
            overwrite_local_file (bool): Whether to overwrite existing local files.
            verbose (bool): Whether to print verbose output.
            dry_run (bool): Whether to perform a dry run (no actual copying).
            filetype_restrictions (list): List of allowed file extensions to copy.

        Returns:
            None
        """
        if dry_run:
            print('Dry run')

        local_root_directory = pjoin(local_root_directory, os.path.basename(remote_root_directory))

        for remote_directory_in_tree in self.walk_remote_tree(remote_root_directory=remote_root_directory):

            local_directory_copy = remote_directory_in_tree.replace(remote_root_directory, local_root_directory)

            if not dry_run:
                os.makedirs(local_directory_copy, exist_ok=True)

            self.ftp.cwd(remote_directory_in_tree)

            filelist = [i for i in self.ftp.mlsd()]

            for f in filelist:
                if f[0].startswith('.'):
                    continue

                if f[1]['type'] == 'file':
                    local_file_copy = pjoin(local_directory_copy, f[0])

                    if not overwrite_local_file and os.path.exists(local_file_copy):
                        continue

                    if local_file_copy.split('.')[-1] in filetype_restrictions or len(filetype_restrictions) == 0:

                        if verbose:
                            print(f'Copying file to: {local_file_copy}')

                        if not dry_run:
                            self.ftp.retrbinary('RETR ' + f[0], open(local_file_copy, 'wb').write)

    def walk_local_tree(self, local_root_directory: str):
        """
        Traverse the local directory tree using breadth-first search and yield each directory path.

        Parameters:
            local_root_directory (str): The root directory on the local system.

        Yields:
            str: The path of each directory in the local tree.
        """
        yield local_root_directory

        queue = [local_root_directory]

        while queue:
            current_directory = queue.pop(0)

            os.chdir(current_directory)

            directory_list = [os.path.basename(i) for i in os.listdir(current_directory) if os.path.isdir(i)]

            for d in directory_list:
                directory_in_tree = pjoin(current_directory, d)
                queue.append(directory_in_tree)
                yield directory_in_tree

    def recursively_copy_files_from_local_directory(self, remote_root_directory: str, local_root_directory: str,
                                                    overwrite_remote_file: bool = False, verbose: bool = False,
                                                    dry_run: bool = False, filetype_restrictions: list = []) -> None:
        """
        Recursively copy files from a local directory to a remote directory using FTPS.

        Parameters:
            remote_root_directory (str): The root directory on the remote FTPS server.
            local_root_directory (str): The root directory for local copies.
            overwrite_remote_file (bool): Whether to overwrite existing remote files.
            verbose (bool): Whether to print verbose output.
            dry_run (bool): Whether to perform a dry run (no actual copying).
            filetype_restrictions (list): List of allowed file extensions to copy.

        Returns:
            None
        """
        if dry_run:
            print('Dry run')

        remote_root_directory = pjoin(remote_root_directory, os.path.basename(local_root_directory))

        for local_directory_in_tree in self.walk_local_tree(local_root_directory=local_root_directory):

            remote_directory_copy = local_directory_in_tree.replace(local_root_directory, remote_root_directory)

            try:
                self.ftp.cwd(remote_directory_copy)

            except error_perm:

                if not dry_run:
                    if verbose:
                        print(f'Making dir: {remote_directory_copy}')
                    self.ftp.mkd(remote_directory_copy)
                else:
                    raise NotImplementedError('Directory doesnt exist and this is a dry run')
                    continue

            filelist = [i for i in os.listdir(local_directory_in_tree) if os.path.isfile(pjoin(local_directory_in_tree, i))]

            remote_filelist = [ri[0] for ri in self.ftp.mlsd() if ri[1]['type'] == 'file']

            for f in filelist:

                if f in remote_filelist:

                    if f.split('.')[-1] in filetype_restrictions or len(filetype_restrictions) == 0:

                        if overwrite_remote_file:

                            if verbose:
                                print(f'Copying file to: {pjoin(remote_directory_copy, f)}')

                            if dry_run:
                                continue

                            with open(pjoin(local_directory_in_tree, f), 'rb') as out_file:
                                self.ftp.storbinary('STOR ' + f, out_file)

    def copy_file_to_remote_directory(self, local_file_path: str, target_remote_directory: str) -> None:
        """
        Copy a file from local directory to a remote directory using FTPS.

        Parameters:
            local_file_path (str): The path of the local file to copy.
            target_remote_directory (str): The target remote directory.

        Returns:
            None
        """
        print(f'Copying {local_file_path} to {target_remote_directory}')

        file_name = os.path.basename(local_file_path)
        try:
            self.ftp.cwd(target_remote_directory)
        except Exception as e:
            print(f'Error: Unable to change to target remote directory {target_remote_directory}. {str(e)}')
            return

        try:
            with open(local_file_path, 'rb') as out_file:
                self.ftp.storbinary('STOR ' + file_name, out_file)
        except Exception as e:
            print(f'Error: Unable to copy the file. {str(e)}')


