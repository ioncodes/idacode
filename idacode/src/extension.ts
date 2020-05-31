import * as vscode from 'vscode';
import * as net from 'net';
import * as path from 'path';
import * as WebSocket from 'ws';

var socket: WebSocket;

function getConfig<T>(name: string) {
    const config = vscode.workspace.getConfiguration('IDACode');
    return config.get(name) as T;
}

function executeScript() {
    const scriptPath = vscode.window.activeTextEditor?.document.uri.fsPath as string;
    
    if (scriptPath !== undefined) {
        const name = path.parse(scriptPath).base;
        socket.send(scriptPath);
        vscode.window.showInformationMessage(`Sent ${name} to IDA`);
    }
}

function connectToIDA() {
    const host = getConfig<string>('host');
    const port = getConfig<number>('port');

    socket = new WebSocket(`ws://${host}:${port}/ws`);

    socket.on('open', () => {
        socket.send('something');
    });
}

export function activate(context: vscode.ExtensionContext) {    
    let commands = [];
    commands.push(vscode.commands.registerCommand('idacode.executeScript', executeScript));
    commands.push(vscode.commands.registerCommand('idacode.connectToIDA', connectToIDA));
    
    for(let command of commands) {
        context.subscriptions.push(command);
    }
}

export function deactivate() {}