import * as vscode from 'vscode';
import * as net from 'net';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
	let disposable = vscode.commands.registerCommand('idacode.executeScript', () => {
		let scriptPath = vscode.window.activeTextEditor?.document.uri.fsPath;
		
		if (scriptPath !== undefined) {
			let client = new net.Socket();
			client.connect(10100, '127.0.0.1', () => {
				scriptPath = scriptPath as string;
				client.write(scriptPath);
				vscode.window.showInformationMessage(`Sent ${path.parse(scriptPath).base} to IDA`);
			});
		}
	});

	context.subscriptions.push(disposable);
}

export function deactivate() {}