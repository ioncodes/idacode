# IDACode

IDACode faciliates the usage and development of IDAPython scripts. It features the execution of Python scripts in your IDA instance and a debugger that allows you to debug your scripts.

## Features

IDACode supports the following main features:

1. Script execution in IDAs environment
2. Debugging scripts with VS Code's remote debugger

![preview](/images/preview.gif)

## Requirements

In order to use IDACode ensure that you have set all necessary information in IDACode's extension settings. For information on how to set up IDACode for IDA please refer to the [project repository](https://github.com/ioncodes/idacode).

## Extension Settings

IDACode requires the following settings to be set in order to function correctly:

* `IDACode.host`: the host address that is running IDA
* `IDACode.port`: the port IDA is listening on
* `IDACode.debug.port`: the debug port the IDAPython debugger is listening on

## Known Issues

IDACode doesn't support host to VM communication unless the VM uses a shared volume that matches the workspace path set in VS Code when connecting to IDA.

## Release Notes

### 0.1.0

- Initial release
- IDAPython remote execution
- IDAPython debugger