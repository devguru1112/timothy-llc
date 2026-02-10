# IDE Setup Guide

## Fixing Pylance Import Errors

If you're seeing import errors like:
- `Import "rest_framework.permissions" could not be resolved`
- `Import "django" could not be resolved`

This is because your IDE needs to be configured to use the correct Python interpreter.

## Solution 1: VS Code / Cursor

### Step 1: Select the Correct Python Interpreter

1. Open Command Palette: `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
2. Type: `Python: Select Interpreter`
3. Choose: `./timothy-llc/backend/venv/Scripts/python.exe` (Windows)
   or: `./timothy-llc/backend/venv/bin/python` (Mac/Linux)

### Step 2: Verify Virtual Environment

Make sure your virtual environment is activated and packages are installed:

```bash
cd timothy-llc/backend
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 3: Reload Window

After selecting the interpreter:
- `Ctrl+Shift+P` → `Developer: Reload Window`

## Solution 2: PyCharm

1. Go to **File → Settings → Project → Python Interpreter**
2. Click the gear icon → **Add**
3. Select **Existing Environment**
4. Browse to: `timothy-llc/backend/venv/Scripts/python.exe` (Windows)
   or: `timothy-llc/backend/venv/bin/python` (Mac/Linux)
5. Click **OK**

## Solution 3: Verify Installation

Test if packages are installed correctly:

```bash
cd timothy-llc/backend
# Activate venv first
python -c "import rest_framework; print('OK')"
python -c "import django; print('OK')"
```

If you get `ModuleNotFoundError`, install packages:

```bash
pip install -r requirements.txt
```

## Common Issues

### Issue: "No module named 'rest_framework'"

**Solution:**
1. Make sure virtual environment is activated
2. Install packages: `pip install -r requirements.txt`
3. Restart IDE

### Issue: IDE still shows errors after installation

**Solution:**
1. Select the correct Python interpreter (see Solution 1)
2. Reload the IDE window
3. Wait for Pylance/Pyright to index packages

### Issue: Multiple Python installations

**Solution:**
- Always use the virtual environment's Python
- Path should include `venv` or `virtualenv` in the path

## Quick Fix Script

Run this to verify everything is set up:

```bash
cd timothy-llc/backend

# Activate venv (Windows)
venv\Scripts\activate

# Or (Mac/Linux)
source venv/bin/activate

# Verify packages
python -c "import django; import rest_framework; print('All packages installed correctly!')"
```

If this works, your packages are installed. The IDE just needs to be pointed to the right interpreter.
