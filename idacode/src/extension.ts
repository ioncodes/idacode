import * as vscode from 'vscode';
import * as path from 'path';
import * as WebSocket from 'ws';
import { Event } from './utils/events';
import './utils/extensions';

var socket: WebSocket;

function getConfig<T>(name: string): T {
    const config = vscode.workspace.getConfiguration('IDACode');
    return config.get(name) as T;
}

function getCurrentDocument(): string {
    return vscode.window.activeTextEditor?.document.uri.fsPath as string;
}

function toBuffer(obj: Object): Buffer {
    return Buffer.from(JSON.stringify(obj));
}

function executeScriptInIDA() {
    const currentDocument = getCurrentDocument();
    const name = path.parse(currentDocument).base;
    socket.send(toBuffer({
        event: Event.ExecuteScript,
        path: currentDocument
    }));
    vscode.window.showInformationMessage(`Sent ${name} to IDA`);
}

function executeScript() {
    if (getConfig<boolean>('saveOnExecute')) {
        vscode.workspace.saveAll().then(executeScriptInIDA);
    } else {
        executeScriptInIDA();
    }
}

function connectToIDA() {
    return new Promise((resolve, reject) => {
        const host = getConfig<string>('host');
        const port = getConfig<number>('port');

        socket = new WebSocket(`ws://${host}:${port}/ws`);

        socket.on('open', async () => {
            const currentDocument = getCurrentDocument();
            const currentFolder = path.parse(currentDocument).dir;
            const workspaceFolder = await vscode.window.showInputBox({
                prompt: 'Enter the path to the folder containing the script',
                value: currentFolder
            });
            socket.send(toBuffer({
                event: Event.SetWorkspace,
                path: workspaceFolder
            }));
            vscode.window.showInformationMessage(`Set workspace folder to ${workspaceFolder}`);
            resolve();
        });

        socket.on('message', data => {
            const message = JSON.parse(data.toString());

            if(message.event === Event.DebuggerReady) {
                const host = getConfig<string>('host');
                const debugPort = getConfig<number>('debug.port');

                vscode.debug.startDebugging(undefined, {
                    name: 'Python: Remote Attach',
                    type: 'python',
                    request: 'attach',
                    port: debugPort,
                    host: host,
                    pathMappings: [
                        {
                            localRoot: '${workspaceFolder}',
                            remoteRoot: '.'
                        }
                    ]
                });
            }
        });
    });
}

function attachToIDA() {
    socket.send(toBuffer({
        event: Event.AttachDebugger
    }));
}

function connectAndAttachToIDA() {
    connectToIDA().then(attachToIDA);
} 

export function activate(context: vscode.ExtensionContext) {    
    let commands = [];
    commands.push(vscode.commands.registerCommand('idacode.executeScript', executeScript));
    commands.push(vscode.commands.registerCommand('idacode.connectToIDA', connectToIDA));
    commands.push(vscode.commands.registerCommand('idacode.attachToIDA', attachToIDA));
    commands.push(vscode.commands.registerCommand('idacode.connectAndAttachToIDA', connectAndAttachToIDA));
    
    for(let command of commands) {
        context.subscriptions.push(command);
    }

    vscode.workspace.onDidSaveTextDocument(() => {
        if (getConfig<boolean>('executeOnSave')) {
            executeScript();
        }
    });
}

export function deactivate() {}