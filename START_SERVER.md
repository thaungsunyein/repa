# 🚀 How to Start the REPA Server

## The Issue

If you get `zsh: command not found: uvicorn`, it means uvicorn is installed but not in your PATH.

## ✅ Solution: Use Python Module Syntax

Instead of:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Use:
```bash
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Quick Start Command

```bash
cd /Users/gildafernandezconchajahnsen/repa
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Alternative: Direct Python Execution

You can also run the app directly:

```bash
cd /Users/gildafernandezconchajahnsen/repa
python3 app.py
```

This will start the server on port 8000 (or the port specified in your `.env` file).

## Verify Server is Running

After starting, you should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Then open: **http://localhost:8000** in your browser.

## Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

## Troubleshooting

### Port Already in Use
If port 8000 is busy, change it:
```bash
python3 -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

Or set PORT in your `.env` file:
```env
PORT=8001
```

### Still Getting Errors
Check that:
- ✅ All environment variables are set in `.env`
- ✅ Database migrations are applied
- ✅ All dependencies are installed: `pip3 install -r requirements.txt`

