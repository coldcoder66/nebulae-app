# Nebulae

In Visual Studio Code, [create a virtual environment](https://code.visualstudio.com/docs/python/environments#_creating-environments). Wait for the environment to be created.

After creation, select the [Python interpreter created](https://code.visualstudio.com/docs/python/environments#_working-with-python-interpreters).

To launch the kivy app, change to the app directory, install requirements, and then run main.py
```bash
cd app
pip install -r requirements.txt
python main.py
```

## Package the Application

### Windows
Build the application using `PyInstaller`. We use the `--log-level=ERROR` to build faster as only error level probalems will print to the console.

```bash
python -m PyInstaller --log-level=ERROR .\intercalm.spec
```

run the application under `.\dist\nebulae\nebulae.exe`.

Now zip the `nebulae` directory and distribute the zip for others to run, 
just unzip the file at destination and run the `nebulae.exe` file, no installation required!