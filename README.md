
# FTPDataExchange

### FTPDataExchange Class Walkthrough:

#### Class Overview:
The `FTPDataExchange` class is designed for managing file transfers and operations to and from Box using FTP using the `ftplib` library.

#### Attributes:
- `host (str)`: The FTP host for the Box account.
- `user (str)`: The FTP username for authentication.
- `password (str)`: The FTP password for authentication.
- `ftp (ftplib.FTP)`: The FTP connection object.

#### Methods:

1. `__init__(self, ftp_host: str, ftp_user: str, ftp_passwd: str)`: Initializes an instance of the class and connects to Box via FTP.

2. `connect_to_remote(self)`: Connects to Box via FTP using the provided credentials.

3. `list_files_remote(self, remote_directory: str = '/') -> list`: Lists files in the specified remote directory on Box via FTP.

4. `walk_remote_tree(self, remote_root_directory: str) -> typing.Generator`: Traverses the remote directory tree using breadth-first search and yields each directory path.

5. `recursively_copy_files_from_remote_directory(self, local_root_directory: str, remote_root_directory: str, overwrite_local_file: bool = False, verbose: bool = False, dry_run: bool = False, filetype_restrictions: list = []) -> None`: Recursively copies files from a remote directory to a local directory using FTP.

6. `walk_local_tree(self, local_root_directory: str)`: Traverses the local directory tree using breadth-first search and yields each directory path.

7. `recursively_copy_files_from_local_directory(self, remote_root_directory: str, local_root_directory: str, overwrite_remote_file: bool = False, verbose: bool = False, dry_run: bool = False, filetype_restrictions: list = []) -> None`: Recursively copies files from a local directory to a remote directory using FTP.

8. `copy_file_to_remote_directory(self, local_file_path: str, target_remote_directory: str) -> None`: Copies a file from a local directory to a remote directory using FTP.

### Code Examples:

#### Example 1: Initializing and Connecting to Box via FTP

```python
import FTPDataExchange
ftp_manager = FTPDataExchange("ftp.box.com", "your_username", "your_password")
ftp_manager.connect_to_remote()
```

#### Example 2: Listing Files in a Remote Directory

```python
files_list = ftp_manager.list_files_remote("/remote_directory")
print(files_list)
```

#### Example 3: Recursively Copying Files from Remote to Local

```python
ftp_manager.recursively_copy_files_from_remote_directory("/local_root", "/remote_root", overwrite_local_file=True, verbose=True, dry_run=False, filetype_restrictions=["txt", "csv"])
```

#### Example 4: Copying a Single File from Local to Remote

```python
ftp_manager.copy_file_to_remote_directory("/local/file/path/file.txt", "/remote/directory")
```
