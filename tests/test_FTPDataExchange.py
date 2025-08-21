#!/usr/bin/env python

"""Tests for `FTPDataExchange` package."""

import pytest
from unittest.mock import patch, Mock


from FTPDataExchange import FTPDataExchange


def test_connect_to_remote_success(ftp_data_exchange):

	
	
	# Mock a successful connection
	with patch.object(ftp_data_exchange.ftp, 'login'):
		ftp_data_exchange.connect_to_remote()

	assert ftp_data_exchange.ftp.login.called
	assert ftp_data_exchange.ftp.set_pasv.called
	assert ftp_data_exchange.ftp.set_pasv.called == 'woo'


@pytest.fixture
def mock_ftp_data_exchange():
	# Create an instance of FTPDataExchange with mock FTP connection
	mock_ftp = Mock()

	with patch('ftplib.FTP') as MockFTP:
		instance = FTPDataExchange('ftp_host', 'ftp_user', 'ftp_passwd')
		instance.ftp = MockFTP.return_value
		yield instance

def test_connect_to_remote_success(ftp_data_exchange):
	# Mock a successful connection
	with patch.object(ftp_data_exchange.ftp, 'login'):
		ftp_data_exchange.connect_to_remote()

	assert ftp_data_exchange.ftp.login.called
	assert ftp_data_exchange.ftp.set_pasv.called
	assert ftp_data_exchange.ftp.set_pasv.called == 'woo'