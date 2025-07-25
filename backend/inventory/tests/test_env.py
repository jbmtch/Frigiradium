import os

def test_env_variable_loaded():
    assert os.getenv('DB_NAME') is not None