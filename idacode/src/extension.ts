import * as vscode from 'vscode';
import * as net from 'net';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
	let disposable = vscode.commands.registerCommand('idacode.executeScript', () => {
		const scriptPath = vscode.window.activeTextEditor?.document.uri.fsPath as string;
		const config = vscode.workspace.getConfiguration('IDACode');
		const host = config.get('host') as string;
		const port = config.get('port') as number;

		if (scriptPath !== undefined) {
			const name = path.parse(scriptPath).base;
			const client = new net.Socket();
			
			client.on('error', _ => {
				vscode.window.showErrorMessage(`Failed sending ${name} to IDA`);
			});

			client.connect(port, host, () => {
				client.write(scriptPath);
				vscode.window.showInformationMessage(`Sent ${name} to IDA`);
			});
		}
	});

	context.subscriptions.push(disposable);
}

export function deactivate() {}