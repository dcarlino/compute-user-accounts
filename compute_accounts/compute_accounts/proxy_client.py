# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Function to fetch information from Compute Accounts proxy server."""

import socket

from . import accounts_proxy
from . import exceptions


def get_account_info(command, timeout=1):
  """Gets output for the given command from the proxy server."""
  sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
  try:
    sock.settimeout(timeout)
    sock.connect(accounts_proxy.UNIX_SOCKET_PATH)
    sock.sendall(command)
    response = []
    data = sock.recv(4096)
    while data:
      response.append(data)
      data = sock.recv(4096)
  finally:
    sock.close()

  lines = ''.join(response).splitlines()
  if not lines:
    raise exceptions.LookupException('Recieved no output.')
  result_code = lines.pop(0)
  if result_code == '404':
    raise exceptions.NotFoundException('Invalid user or group.')
  elif result_code != '200':
    raise exceptions.LookupException('Command [{}] failed with code [{}].',
                                     command, result_code)

  return lines
