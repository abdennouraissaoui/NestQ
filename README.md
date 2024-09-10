## Development Setup

### Running Python Scripts in VS Code

To ensure you can run Python scripts from any directory within this project (similar to PyCharm’s "Sources Root"), follow these steps:

1. **Configure PYTHONPATH**:
   - Create a `.env` file in the root of the project (if not already created) and add the following line:
     ```bash
     PYTHONPATH=.
     PYTHONDONTWRITEBYTECODE=1
     ```

2. **VS Code Settings**:
   - In the root of the project, create a `.vscode/settings.json` file with the following content:
     ```json
     {
         "python.envFile": "${workspaceFolder}/.env",
         "jupyter.notebookFileRoot": "${workspaceFolder}"
     }
     ```
     The `jupyter.notebookFileRoot` setting ensures that any Jupyter notebooks opened in VS Code use the project root as the base directory for relative paths.

3. **Configure `launch.json` for Debugging**:
   - In the `.vscode` folder, create or update the `launch.json` file with the following configuration:
     ```json
     {
         "version": "0.2.0",
         "configurations": [
             {
                 "name": "Python: Current File",
                 "type": "debugpy",
                 "request": "launch",
                 "program": "${file}",
                 "console": "integratedTerminal",
                 "env": {
                     "PYTHONPATH": "${workspaceFolder}",
                     "PYTHONDONTWRITEBYTECODE": "1"
                 }
             }
         ]
     }
     ```
     This ensures that when running or debugging Python scripts, the `PYTHONPATH` is set correctly, so imports work as expected.

4. **Using Absolute Imports**:
   - Make sure to use absolute imports in your Python files. For example, in `train.py`, you can import from `models` like this:
     ```python
     from models.test import hello
     ```

5. **Restart VS Code**:
   - After making these changes, restart VS Code to ensure all settings are loaded correctly.

Now, with these steps, you can run any Python script and Jupyter notebooks from within the project without manually adjusting the working directory.

### Additional Notes
- This setup ensures that the `PYTHONPATH` is set correctly for the project, allowing VS Code to recognize the modules and imports from the root directory.
- The `jupyter.notebookFileRoot` setting ensures that relative paths in notebooks are resolved from the project root.
- To automatically create __init__.py files in folders, install the "Python init Generator" extension in VS Code