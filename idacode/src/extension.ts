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

function executeScript() {
    const currentDocument = getCurrentDocument();
    const name = path.parse(currentDocument).base;
    socket.send(currentDocument);
    vscode.window.showInformationMessage(`Sent ${name} to IDA`);
}

function connectToIDA() {
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
        socket.send({
            event: Event.SetWorkspace,
            folder: workspaceFolder
        }.toBuffer());
        vscode.window.showInformationMessage(`Set workspace folder to ${workspaceFolder}`);
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