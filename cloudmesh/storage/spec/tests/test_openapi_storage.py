###############################################################
# pip install .; pytest -v --capture=no -v --nocapture tests/test_cloud_openapi_azure_storage.py:Test_cloud_openapi_azure_storage.test_001
# pytest -v --capture=no tests/test_openapi_azure_storage.py
# pytest -v  tests/test_openapi_azure_storage.py
###############################################################

from __future__ import print_function

import os
import time
import requests

import pytest
from cloudmesh.common.run.background import run
from cloudmesh.common.util import banner
from cloudmesh.shell.variables import Variables
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import path_expand
from  pathlib import Path
from cloudmesh.common.util import writefile

pytest.storage = None
pytest.openapi = None


# noinspection PyPep8
@pytest.mark.incremental
class Test_cloud_storage:
    """

    see: https://github.com/cloudmesh/cloudmesh-common/blob/master/cloudmesh/common/run/background.py
    the code in thel link has not bean tested
    make this s function execute the server in the back ground not in a termina,
    get the pid and kill it after the test is done
    UNAME := $(shell uname)
    ifeq ($(UNAME), Darwin)
    define terminal
      osascript -e 'tell application "Terminal" to do script "cd $(PWD); $1"'
    endef
    endif
    ifeq ($(UNAME), Linux)
    define terminal
      gnome-terminal --command 'bash -c "cd $(PWD); $1"'
    endef
    endif
    """

    def create_file(self, location, content):
        d = Path(os.path.dirname(path_expand(location)))
        print()
        print("TESTDIR:", d)

        d.mkdir(parents=True, exist_ok=True)

        writefile(path_expand(location), content)

    def test_setup(self):
        self.variables = Variables()
        self.storages = Parameter.expand(self.variables['storage'])
        pytest.storage = self.storages[0]
        command = ['python', 'server.py']
        pytest.openapi = run(command)
        pytest.openapi.execute()
        print(pytest.openapi.pid)
        time.sleep(5)

    def test_install(self):
        time.sleep(3)

    def test_01_create_source(self):
        # create source dir
        self.create_file("~/openapi/a.txt", "content of a")
        assert True

    def test_openapi_storage_create(self):
        banner('create the directory')
        storage = pytest.storage
        response = requests.get(
            f"http://localhost:8080/cloudmesh/create_dir?service={storage}&directory=%2fapitest")
        print(response)
        print()

    def test_openapi_storage_put(self):
        banner('Put/Upload the blobs')
        storage = pytest.storage
        headers = {
            'Content-Type': 'application/json',
        }
        data = '{"service": "azureblob", "source": "~/openapi/a.txt", "destination": "/apitest", "recursive": "False"}'
        response = requests.post('http://localhost:8080/cloudmesh/put_blob', headers=headers, data=data)
        print(response)
        print()

    def test_openapi_storage_get(self):
        banner('get the blobs')
        storage = pytest.storage
        response = requests.get(
            f"http://localhost:8080/cloudmesh/get_blob?service={storage}&source=%7e%2fopenapi&destination=%2fapitest%2fa%2etxt")
        print(response)
        print()

    def test_openapi_storage_list(self):
        banner('List the blobs')
        storage = pytest.storage
        response = requests.get(
            f"http://localhost:8080/cloudmesh/list_blob?service={storage}&directory=%2fapitest&recursive=True")
        print(response)
        print()

    def test_openapi_storage_search(self):
        banner('search the blobs')
        storage = pytest.storage
        response = requests.get(
            f"http://localhost:8080/cloudmesh/search_blob?service={storage}&directory=%2fapitest&filename=a%2etxt")
        print(response)
        print()

    def test_openapi_storage_del(self):
        banner('delete the blobs')
        storage = pytest.storage
        response = requests.get(
            f"http://localhost:8080/cloudmesh/delete_blob?service={storage}&source=%2fapitest%2fa%2etxt")
        print(response)
        print()

    def test_kill_pid(self):
        pytest.openapi.kill()
