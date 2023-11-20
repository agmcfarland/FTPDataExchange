

# Create environment

```sh
conda create -n FTPDataExchange_env
conda activate FTPDataExchange_env
conda install -c anaconda ipython
pip install pytest
pip install pytest-mock
```

# Test

```sh
cd /Users/agmcfarland/Dropbox/Documents/bushman_lab/FTPDataExchange/tests
```

```sh
pytest test_FTPDataExchange.py
```

```python
box_project_server = FTPDataExchange(
	ftp_host = 'ftp.box.com',
	ftp_user = 'agmcfar@upenn.edu',
	ftp_passwd = 'MyStupidBoxPwardIsStupid123!@#')

box_project_server.list_files_remote('/U01_bnAb_escape')
```