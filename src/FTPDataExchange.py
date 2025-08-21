from ftplib import FTP_TLS, error_perm
from os.path import join as pjoin
import os
import typing
from contextlib import contextmanager


class FTPDataExchange:
	"""
	A class for managing file transfers and operations on Box using FTPS.
	"""

	def __init__(self, ftp_host: str, ftp_user: str, ftp_passwd: str):
		self.host = ftp_host
		self.user = ftp_user
		self.password = ftp_passwd

	@contextmanager
	def _ftp_connection(self):
		ftp = FTP_TLS(self.host)
		ftp.login(self.user, self.password)
		ftp.prot_p()
		ftp.set_pasv(True)
		try:
			yield ftp
		finally:
			ftp.quit()

	def list_files_remote(self, remote_directory: str = "/") -> list:
		"""List files in a remote directory."""
		with self._ftp_connection() as ftp:
			ftp.cwd(remote_directory)
			file_list = []
			ftp.retrlines("LIST", lambda x: file_list.append(x.split()[-1]))
			return file_list

	def _walk_remote_tree(
		self,
		remote_root_directory: str,
		ftp: FTP_TLS,
	) -> typing.Generator:
		"""
		Yield each directory in the remote tree (BFS).
		Requires an already-open FTP connection.
		"""
		yield remote_root_directory
		queue = [remote_root_directory]
		while queue:
			current_directory = queue.pop(0)
			ftp.cwd(current_directory)
			for name, facts in ftp.mlsd():
				if name.startswith("."):
					continue
				if facts["type"] == "dir":
					directory_in_tree = pjoin(current_directory, name)
					queue.append(directory_in_tree)
					yield directory_in_tree

	def recursively_copy_files_from_remote_directory(
		self,
		local_root_directory: str,
		remote_root_directory: str,
		overwrite_local_file: bool = False,
		verbose: bool = False,
		dry_run: bool = False,
		filetype_restrictions: list = [],
	) -> None:
		"""Recursively copy files from remote to local."""
		if dry_run:
			print("Dry run")

		local_root_directory = pjoin(local_root_directory, os.path.basename(remote_root_directory))

		with self._ftp_connection() as ftp:
			for remote_directory_in_tree in self._walk_remote_tree(remote_root_directory, ftp):
				local_directory_copy = remote_directory_in_tree.replace(
					remote_root_directory, local_root_directory
				)

				if not dry_run:
					os.makedirs(local_directory_copy, exist_ok=True)

				ftp.cwd(remote_directory_in_tree)
				for name, facts in ftp.mlsd():
					if name.startswith(".") or facts["type"] != "file":
						continue

					local_file_copy = pjoin(local_directory_copy, name)

					if not overwrite_local_file and os.path.exists(local_file_copy):
						continue

					if (
						name.split(".")[-1] in filetype_restrictions
						or not filetype_restrictions
					):
						if verbose:
							print(f"Copying file to: {local_file_copy}")

						if not dry_run:
							with open(local_file_copy, "wb") as out_file:
								ftp.retrbinary("RETR " + name, out_file.write)

	def walk_local_tree(self, local_root_directory: str):
		"""Yield each directory in the local tree (BFS)."""
		yield local_root_directory
		queue = [local_root_directory]
		while queue:
			current_directory = queue.pop(0)
			for entry in os.listdir(current_directory):
				full_path = pjoin(current_directory, entry)
				if os.path.isdir(full_path):
					queue.append(full_path)
					yield full_path

	def recursively_copy_files_from_local_directory(
		self,
		remote_root_directory: str,
		local_root_directory: str,
		overwrite_remote_file: bool = False,
		verbose: bool = False,
		dry_run: bool = False,
		filetype_restrictions: list = [],
	) -> None:
		"""Recursively copy files from local to remote."""
		if dry_run:
			print("Dry run")

		remote_root_directory = pjoin(remote_root_directory, os.path.basename(local_root_directory))

		with self._ftp_connection() as ftp:
			for local_directory_in_tree in self.walk_local_tree(local_root_directory):
				remote_directory_copy = local_directory_in_tree.replace(
					local_root_directory, remote_root_directory
				)

				try:
					ftp.cwd(remote_directory_copy)
				except error_perm:
					if not dry_run:
						if verbose:
							print(f"Making dir: {remote_directory_copy}")
						ftp.mkd(remote_directory_copy)
					else:
						raise NotImplementedError("Directory doesnt exist and this is a dry run")

				filelist = [
					i
					for i in os.listdir(local_directory_in_tree)
					if os.path.isfile(pjoin(local_directory_in_tree, i))
				]

				remote_filelist = [ri[0] for ri in ftp.mlsd() if ri[1]["type"] == "file"]

				for f in filelist:
					if (
						f.split(".")[-1] in filetype_restrictions
						or not filetype_restrictions
					):
						if f in remote_filelist and not overwrite_remote_file:
							continue
						if verbose:
							print(f"Copying file to: {pjoin(remote_directory_copy, f)}")
						if dry_run:
							continue
						with open(pjoin(local_directory_in_tree, f), "rb") as out_file:
							ftp.storbinary("STOR " + f, out_file)

	def copy_file_to_remote_directory(self, local_file_path: str, target_remote_directory: str) -> None:
		"""Copy a single file from local to remote."""
		file_name = os.path.basename(local_file_path)
		with self._ftp_connection() as ftp:
			try:
				ftp.cwd(target_remote_directory)
				with open(local_file_path, "rb") as out_file:
					ftp.storbinary("STOR " + file_name, out_file)
				print(f"Copied {local_file_path} → {target_remote_directory}")
			except Exception as e:
				print(f"Error: {str(e)}")

	def copy_file_to_local_directory(self, local_directory: str, remote_file_path: str) -> None:
		"""Copy a single file from remote to local."""
		file_name = os.path.basename(remote_file_path)
		with self._ftp_connection() as ftp:
			try:
				with open(pjoin(local_directory, file_name), "wb") as out_file:
					ftp.retrbinary("RETR " + remote_file_path, out_file.write)
				print(f"Copied {remote_file_path} → {local_directory}")
			except Exception as e:
				print(f"Error: {str(e)}")
