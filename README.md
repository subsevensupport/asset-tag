# Asset Tag Service

A simple, reliable REST API service for generating sequential asset tag numbers. Built with FastAPI and SQLite, this service ensures globally unique identifiers for asset management systems.

## Features

- **Sequential number generation** - Generates unique sequential numbers starting from 0
- **Thread-safe operations** - Handles concurrent requests safely using SQLite transactions
- **Persistent storage** - Numbers persist across service restarts
- **Basic authentication** - Two-tier access control:
  - Admin access for generating new numbers
  - Read-only access for checking the next number without consuming it
- **Auto-generated API documentation** - Interactive docs at `/docs` and `/redoc`
- **Zero-padded formatting ready** - Returns raw integers that can be formatted as needed (e.g., 0047, 0001)

## Quick Start

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd asset-tag-service
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your credentials:
   ```env
   ASSET_TAG_USERNAME=admin
   ASSET_TAG_PASSWORD=your-secure-password-here
   ASSET_TAG_READONLY_USERNAME=reader
   ASSET_TAG_READONLY_PASSWORD=different-password-here
   ```

5. Run the service:
   ```bash
   uvicorn main:app --reload
   ```

6. Access the service:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## API Endpoints

### `GET /`
Health check endpoint that returns a welcome message.

**Response:**
```json
{
  "message": "Asset Tag Service is running"
}
```

### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy"
}
```

### `GET /next-number`
Get the next asset tag number (increments the counter).

**Authentication:** Requires admin credentials (Basic Auth)

**Response:**
```json
{
  "number": 42
}
```

### `GET /peek-next-number`
Check what the next number will be without consuming it.

**Authentication:** Requires read-only credentials (Basic Auth)

**Response:**
```json
{
  "number": 42
}
```

## Usage Example

### PowerShell Script
```powershell
$uri = "http://your-server:8000/next-number"
$cred = Get-Credential -UserName "admin"
$response = Invoke-RestMethod -Uri $uri -Authentication Basic -Credential $cred
$assetNumber = $response.number.ToString().PadLeft(4, '0')
$computerName = "DESK-$assetNumber"
Write-Host "New computer name: $computerName"
```

### Python Client
```python
import requests
from requests.auth import HTTPBasicAuth

# Get next number
response = requests.get(
    'http://your-server:8000/next-number',
    auth=HTTPBasicAuth('admin', 'your-password')
)
asset_number = response.json()['number']
computer_name = f"DESK-{asset_number:04d}"
print(f"New computer name: {computer_name}")
```

### curl Example
```bash
# Get next number
curl -u admin:password http://localhost:8000/next-number

# Peek at next number (read-only)
curl -u reader:password http://localhost:8000/peek-next-number
```

## Deployment with Docker

### Using Docker Compose with Ansible

If you're deploying with Ansible and Docker Compose, add these environment variables to your compose file:

```yaml
services:
  asset-tag-service:
    image: your-image-name
    ports:
      - "8000:8000"
    environment:
      - "ASSET_TAG_USERNAME={{ asset_tagger_api_user }}"
      - "ASSET_TAG_PASSWORD={{ asset_tagger_api_password }}"
      - "ASSET_TAG_READONLY_USERNAME={{ asset_tagger_readonly_user }}"
      - "ASSET_TAG_READONLY_PASSWORD={{ asset_tagger_readonly_password }}"
    volumes:
      - ./data:/app/data  # Persist SQLite database
```

### Building Docker Image

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t asset-tag-service .
docker run -p 8000:8000 \
  -e ASSET_TAG_USERNAME=admin \
  -e ASSET_TAG_PASSWORD=secret \
  -e ASSET_TAG_READONLY_USERNAME=reader \
  -e ASSET_TAG_READONLY_PASSWORD=readonly \
  asset-tag-service
```

## Configuration

All configuration is done through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ASSET_TAG_USERNAME` | Username for admin access | `admin` |
| `ASSET_TAG_PASSWORD` | Password for admin access | (required) |
| `ASSET_TAG_READONLY_USERNAME` | Username for read-only access | `reader` |
| `ASSET_TAG_READONLY_PASSWORD` | Password for read-only access | (required) |

## Database

The service uses SQLite for persistent storage. The database file `asset_tags.db` is created automatically on first run.

### Database Schema
```sql
CREATE TABLE counters (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    current_value INTEGER NOT NULL DEFAULT 0
);
```

The `CHECK (id = 1)` constraint ensures only one row exists, maintaining a single counter.

## Security Considerations

1. **Never commit `.env` files** - Added to `.gitignore`
2. **Use strong passwords** - Especially in production
3. **HTTPS in production** - Use a reverse proxy (nginx, Traefik) with SSL
4. **Separate credentials** - Admin vs read-only access
5. **Environment variables** - Credentials are never hardcoded

## Troubleshooting

### Database locked errors
SQLite handles concurrent access well, but under extreme load you might see "database is locked" errors. The service uses thread-local connections to minimize this risk.

### Number sequence gaps
If a client receives a number but fails to use it (e.g., network error), that number is still consumed. This is by design to ensure uniqueness.

### Resetting the counter
To reset the counter, stop the service and delete `asset_tags.db`. The counter will start from 0 again on next startup.

## Development

### Project Structure
```
asset-tag-service/
├── main.py           # FastAPI application
├── database.py       # SQLite database operations
├── requirements.txt  # Python dependencies
├── .env             # Local environment variables (not in git)
├── .gitignore       # Git ignore file
└── asset_tags.db    # SQLite database (created at runtime)
```

### Running Tests
```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

