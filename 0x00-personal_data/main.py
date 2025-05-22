#!/usr/bin/env python3
"""
Main file
"""

hash_password = __import__('encrypt_password').hash_password
is_valid = __import__('encrypt_password').is_valid

password = "MyAmazingPassw0rd"

print(is_valid(b'$2b$12$q7Kr/lLA8WQMJ7tFtbN70uKs7ptdxUdOrIoKasQEM0xJ2DcDDfCby', password))
