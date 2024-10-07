## Development Setup

### Getting Started

Follow these steps to get started with the project:

1. **Clone the Repository**:
   - Open your terminal and run the following command to clone the repository:
     ```bash
     git clone https://github.com/abdennouraissaoui/NestQ.git
     ```

2. **Navigate to the Project Directory**:
   - Change to the project directory:
     ```bash
     cd NestQ
     ```

3. **Create a New Environment**:
   - Create a new virtual environment. You can use `venv` or any other environment management tool you prefer. Here’s how to do it with `venv`:
     ```bash
     python -m venv venv
     ```

4. **Activate the Environment**:
   - Activate the virtual environment:
     - **Windows**:
       ```bash
       venv\Scripts\activate
       ```
     - **Linux/MacOS**:
       ```bash
       source venv/bin/activate
       ```

5. **Install Requirements**:
   - Install the necessary dependencies by running:
     ```bash
     pip install -r requirements.txt
     ```

### Configuration File

1. **Rename Configuration File**:
   - Rename `@sample_nestq.ini` to `nestq.ini`, and contact admin to get the API keys.

### Python Version and Dependencies

- **Python Version**:
  - Use Python 3.12 for this project.

### Environment Variable Configuration

- To set the environment for the application, you need to define the `NESTQ_ENV` variable. This variable determines whether the application runs in development or production mode.

  **Windows:**
  ```bash
  set NESTQ_ENV=development  # for development
  set NESTQ_ENV=production   # for production
  ```

  **Linux/MacOS:**
  ```bash
  export NESTQ_ENV=development  # for development
  export NESTQ_ENV=production   # for production
  ```

- Ensure to set this variable before running the application to load the appropriate configuration settings.

### Running Python Scripts in Cursor

To ensure you can run Python scripts from any directory within this project (similar to PyCharm’s "Sources Root"), follow these steps:

1. **Configure PYTHONPATH**:
   - Create a `.env` file in the root of the project (if not already created) and add the following line:
     ```bash
     PYTHONPATH=.
     PYTHONDONTWRITEBYTECODE=1
     ```

2. **Cursor Settings**:
   - In the root of the project, create a `.vscode/settings.json` file with the following content:
     ```json
     {
         "python.envFile": "${workspaceFolder}/.env",
         "jupyter.notebookFileRoot": "${workspaceFolder}"
     }
     ```
     The `jupyter.notebookFileRoot` setting ensures that any Jupyter notebooks opened in Cursor use the project root as the base directory for relative paths.

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

5. **Restart Cursor**:
   - After making these changes, restart Cursor to ensure all settings are loaded correctly.

### Additional Notes

- This setup ensures that the `PYTHONPATH` is set correctly for the project, allowing Cursor to recognize the modules and imports from the root directory.
- The `jupyter.notebookFileRoot` setting ensures that relative paths in notebooks are resolved from the project root.
- To automatically create `__init__.py` files in folders, install the "Python init Generator" extension in Cursor.

### Recommended IDE

- The recommended IDE for this project is **Cursor AI**. If it's your first time using it, I recommend watching these two videos to help you get started with Python:
  1. **Features of Cursor**: [Watch here](https://www.youtube.com/watch?v=CqkZ-ybl3lg&t=785s)
  2. **How to Set It Up**: [Watch here](https://youtu.be/mpk4Q5feWaw?si=z7sXrhh4PDTpyXu2)