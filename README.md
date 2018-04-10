# Python Command Line worker
Worker to execute commands

Dependencies
------------

Depends on [py_amqp_connection](https://github.com/FTV-Subtil/py_amqp_connection) package:
```bash
pip3 install amqp_connection
```

Usage
-----

Example of handled AMQP message body:

```json
{
  "job_id": "1",
  "parameters": {
    "requirements": {
      "paths": [
        "/path/to/required/file"
      ]
    },
    "program": "/path/to/exe",
    "inputs": [
      {
        "path": "/path/to/source/file",
        "options": {
          ...
        }
      },
      ...
    ],
    "outputs": [
      {
        "path": "/path/to/destination/file",
        "options": {
          ...
        }
      },
      ...
    ]
  }
}
```

The resulting command will be constructed as follow: `program` `inputs_options` `inputs_path` ... `outputs_options` `outputs_path`

For example:
```json
{
  ...
  "parameters": {
    ...
    "program": "/bin/cp",
    "inputs": [
      {
        "path": "/tmp/dir_1",
        "options": {
          "-R": true
        }
      }
    ],
    "outputs": [
      {
        "path": "/tmp/dir_2",
        "options": {}
      }
    ]
  }
}
```

This message will trigger the execution of: `/bin/cp -R /tmp/dir_1 /tmp/dir_2`

__Note__ that the executable directory can be set directly in the `program` message parameter, or as value of the environment variable `COMMAND_BIN_PATH`. The default value is `/usr/bin`.

The library path can be indicated as well as a message parameter:
```json
...
  "libraries": [
    "/usr/local/lib",
    "/opt/my_program/lib",
    ...
  ]
```

The paths will be that way added to the `LD_LIBRARY_PATH` environment variable.
