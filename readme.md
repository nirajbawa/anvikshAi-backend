# Anviksh AI API Setup Guide

This guide walks you through setting up a Python virtual environment, installing dependencies using `requirements.txt`, and running a FastAPI application.

## Prerequisites

- Python 3.12.3 installed
- `pip` (Python package manager) installed

## Setting Up a Virtual Environment

To create and activate a virtual environment, follow these steps:

### On Windows (CMD/PowerShell):
```sh
python -m venv venv
venv\Scripts\activate
```

### On macOS/Linux:
```sh
python3 -m venv venv
source venv/bin/activate
```

## Installing Dependencies

Once the virtual environment is activated, install the required dependencies using:
```sh
pip install -r requirements.txt
```

## Running the FastAPI Application

Run the FastAPI application using Uvicorn:
```sh
fastapi dev main.py
OR
uvicorn main:app
```

## Verifying the Setup

Once the server is running, open your browser or use an API client (like Postman) to access:
- API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Deactivating the Virtual Environment

When you're done, deactivate the virtual environment with:
```sh
deactivate
```

## Additional Notes

- If `pip` is outdated, upgrade it using:
  ```sh
  pip install --upgrade pip
  ```
- To export dependencies, use:
  ```sh
  pip freeze > requirements.txt
  ```
- For production, consider running Uvicorn with Gunicorn:
  ```sh
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
  ```

