# Nebulae

In Visual Studio Code, [create a virtual environment](https://code.visualstudio.com/docs/python/environments#_creating-environments). Wait for the environment to be created.

After creation, select the [Python interpreter created](https://code.visualstudio.com/docs/python/environments#_working-with-python-interpreters).

To launch the kivy app, change to the app directory, install requirements, and then run main.py
```bash
cd app
pip install -r requirements.txt
python main.py
```

## Azure AI Foundry Assistant Setup

The Assistant screen authenticates to Azure AI Foundry by using `DefaultAzureCredential`.

For local development, use one of these authentication options:

1. Sign in with Azure CLI:
```bash
az login
```
2. Or provide a service principal in your environment:
```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_SECRET=<client-secret>
```

Optional environment variables for the Nebulae assistant:

```bash
AZURE_AI_PROJECT_ENDPOINT=https://fndry-nebulae-east.services.ai.azure.com/api/projects/project-nebulae
NEBULAE_AGENT_NAME=nebulae-agent
NEBULAE_AGENT_VERSION=1
AZURE_IDENTITY_LOG_LEVEL=DEBUG
```

Notes:

- `AZURE_AI_PROJECT_ENDPOINT`, `NEBULAE_AGENT_NAME`, and `NEBULAE_AGENT_VERSION` default to the current Nebulae Foundry project values if they are not set.
- The Assistant screen sends the full local conversation history on each turn so the Nebulae agent can answer iteratively.
- If Azure CLI was just installed or upgraded, restart VS Code before debugging so `DefaultAzureCredential` can find `az` on `PATH`.
- Packaged end-user sign-in is not implemented yet. The current app flow is intended for local and developer-managed Azure authentication.

## Package the Application

### Windows
Build the application using `PyInstaller`. We use the `--log-level=ERROR` to build faster as only error level probalems will print to the console.

```bash
python -m PyInstaller --log-level=ERROR .\intercalm.spec
```

run the application under `.\dist\nebulae\nebulae.exe`.

Now zip the `nebulae` directory and distribute the zip for others to run, 
just unzip the file at destination and run the `nebulae.exe` file, no installation required!