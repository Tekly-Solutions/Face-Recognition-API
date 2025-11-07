# 🐳 Docker Compose - Complete Run Guide

## 📋 Quick Start (Copy & Paste)

### **Windows (CMD)**

```cmd
c
```

### **macOS/Linux (Terminal)**

```bash
cd Backend
docker-compose up --build -d
```

---

## 🚀 Step-by-Step Commands

### **Step 1: Navigate to Backend Folder**

**Windows (CMD):**

```cmd
cd C:\Users\yasiru\Desktop\Face-Recognition-API\Backend
```

**macOS/Linux:**

```bash
cd ~/Desktop/Face-Recognition-API/Backend
```

### **Step 2: Build and Start the Container**

**Option A: Build and Run in Background (RECOMMENDED)**

```bash
docker-compose up --build -d
```

- `--build` = Build image from scratch
- `-d` = Detached mode (runs in background)

**Option B: Build and Run in Foreground (See Logs)**

```bash
docker-compose up --build
```

- Shows all logs in terminal
- Press `Ctrl+C` to stop

**Option C: If Image Already Built**

```bash
docker-compose up -d
```

- Just runs the container
- Skips building if image exists

---

## ✅ Verify It's Running

### **Check Container Status**

```bash
docker-compose ps
```

**Expected Output:**

```
NAME                    STATUS              PORTS
face-recognition-api    Up X seconds        0.0.0.0:8000->8000/tcp
```

### **Test API Health**

**Option 1: Using curl (Windows/Mac/Linux)**

```bash
curl http://localhost:8000/health
```

**Option 2: Using PowerShell (Windows)**

```powershell
Invoke-WebRequest http://localhost:8000/health
```

**Option 3: Using browser**

- Open: `http://localhost:8000/health`

**Expected Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_ready": true,
  "ready": true
}
```

---

## 📊 Useful Commands

### **View Live Logs**

```bash
docker-compose logs -f
```

- `-f` = Follow (live updates)
- Press `Ctrl+C` to exit

### **View Logs from Specific Service**

```bash
docker-compose logs -f backend
```

### **View Last 50 Lines of Logs**

```bash
docker-compose logs --tail=50
```

### **Stop Container (Keep Image)**

```bash
docker-compose stop
```

### **Start Container Again**

```bash
docker-compose start
```

### **Stop and Remove Container**

```bash
docker-compose down
```

- Container is deleted
- Image remains (can rebuild from it)

### **Stop and Remove Container + Image**

```bash
docker-compose down --rmi all
```

- Removes container AND image
- Will rebuild next time

### **Remove Everything (Clean Slate)**

```bash
docker-compose down --rmi all -v
```

- `-v` = Remove volumes (dataset, models, logs)
- **WARNING:** Deletes all trained models!

### **Rebuild Image**

```bash
docker-compose build --no-cache
```

- `--no-cache` = Ignore cached layers, rebuild from scratch

---

## 🔍 Access the API

### **1. Swagger Documentation (Interactive)**

```
http://localhost:8000/docs
```

- Try all endpoints in browser
- See request/response schemas

### **2. ReDoc Documentation**

```
http://localhost:8000/redoc
```

- Read-only API documentation

### **3. OpenAPI Schema (JSON)**

```
http://localhost:8000/openapi.json
```

---

## 🧪 Test API Endpoints

### **Check Health Status**

```bash
curl http://localhost:8000/health
```

### **Check Database**

```bash
curl http://localhost:8000/database
```

### **Train a Person (Example)**

```bash
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d "{
    \"person_name\": \"John Doe\",
    \"images\": [\"base64_image_1\", \"base64_image_2\"]
  }"
```

### **Verify a Face (Example)**

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d "{
    \"image\": \"base64_image\",
    \"threshold\": 0.6
  }"
```

### **Download from Firebase**

```bash
curl -X POST http://localhost:8000/firebase/download
```

---

## 🛠️ Troubleshooting

### **Problem: Port 8000 Already in Use**

**Option 1: Change Port in docker-compose.yml**

```yaml
ports:
  - "8001:8000" # Use 8001 instead of 8000
```

Then access API at: `http://localhost:8001`

**Option 2: Find and Kill Process Using Port 8000**

**Windows (PowerShell):**

```powershell
Get-Process | Where-Object {$_.Name -like "*python*"} | Stop-Process -Force
```

**macOS/Linux:**

```bash
lsof -i :8000
kill -9 <PID>
```

### **Problem: Docker Not Installed**

**Windows:**

- Download: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- Install and restart

**macOS:**

- Download: [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
- Install and restart

**Linux:**

```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

### **Problem: "docker-compose: command not found"**

**Windows:**

- Open PowerShell as Admin
- Reinstall Docker Desktop
- Restart terminal

**macOS/Linux:**

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### **Problem: Container Stops Immediately**

**Check logs:**

```bash
docker-compose logs
```

**Common issues:**

- Missing `ServiceAccountKey.json` (Firebase)
- Insufficient memory
- Port already in use

### **Problem: "Cannot connect to Docker daemon"**

**Windows/macOS:**

- Open Docker Desktop application
- Wait for it to fully load
- Try command again

**Linux:**

```bash
sudo systemctl start docker
```

### **Problem: Out of Memory**

**Increase Docker Memory Limit:**

**Windows/macOS (Docker Desktop):**

1. Open Docker Desktop
2. Settings → Resources
3. Increase Memory to 4GB or more
4. Restart Docker

**Linux:**

```bash
# Check current memory
docker stats

# Increase in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

---

## 📦 Environment Variables

The docker-compose.yml sets these automatically:

```yaml
environment:
  - PORT=8000
  - ENV=production
  - PYTHONUNBUFFERED=1
  - PYTHONDONTWRITEBYTECODE=1
```

**To override, create `.env` file in Backend folder:**

```
PORT=8000
ENV=production
FIREBASE_CONFIG_PATH=/app/ServiceAccountKey.json
DATASET_PATH=/app/dataset
MODELS_PATH=/app/models
```

---

## 📂 Persistent Data (Volumes)

The docker-compose.yml mounts these directories:

| Volume      | Purpose                        |
| ----------- | ------------------------------ |
| `./dataset` | Trained faces (images)         |
| `./models`  | Saved embeddings & FAISS index |
| `./logs`    | Application logs               |
| `./config`  | Configuration files            |

**Data persists even after container stops!**

---

## 🔄 Common Workflows

### **Complete Fresh Start**

```bash
# Stop and remove everything
docker-compose down --rmi all -v

# Rebuild and start
docker-compose up --build -d

# Check status
docker-compose ps
```

### **Restart Container**

```bash
# Stop
docker-compose stop

# Start again
docker-compose start

# Or restart in one command
docker-compose restart
```

### **Deploy with New Image**

```bash
# Pull latest code
git pull

# Rebuild image
docker-compose build --no-cache

# Stop old container
docker-compose stop

# Start new container
docker-compose up -d
```

### **Debug Mode (View Logs)**

```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Logs from specific time
docker-compose logs --since 10m
```

---

## 🚦 Container States

| Command                  | Effect         | Container Status |
| ------------------------ | -------------- | ---------------- |
| `docker-compose up -d`   | Start          | ✅ Running       |
| `docker-compose stop`    | Pause          | ⏸️ Stopped       |
| `docker-compose start`   | Resume         | ✅ Running       |
| `docker-compose restart` | Restart        | ✅ Running       |
| `docker-compose down`    | Stop + Delete  | ❌ Removed       |
| `docker-compose pause`   | Freeze process | ⏸️ Paused        |
| `docker-compose unpause` | Unfreeze       | ✅ Running       |

---

## 📊 Monitor Container

### **View Resource Usage**

```bash
docker stats
```

Shows: CPU, Memory, Network I/O

### **View Container Details**

```bash
docker-compose ps -a
```

### **Inspect Container**

```bash
docker inspect face-recognition-api
```

### **Execute Command Inside Container**

```bash
docker-compose exec backend bash
```

- Now you're inside the container!
- Run Python commands, check files, etc.
- Type `exit` to leave

---

## 🔐 Security Best Practices

### **1. Use `.env` File for Secrets**

```bash
# .env file (DO NOT COMMIT)
FIREBASE_KEY_PATH=/app/ServiceAccountKey.json
API_KEY=your-secret-key
```

### **2. Limit Container Resources**

```yaml
deploy:
  resources:
    limits:
      cpus: "2.0"
      memory: 4G
    reservations:
      cpus: "1.0"
      memory: 2G
```

### **3. Run as Non-Root User**

```yaml
user: "1000" # Non-root user ID
```

### **4. Use Health Checks**

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 🎯 Production Deployment

### **For Production Use:**

```bash
# Build optimized image
docker-compose -f docker-compose.yml build --no-cache

# Run with restart policy
docker-compose up -d --restart=always

# Monitor
docker-compose logs -f
```

### **With Load Balancer (Multiple Instances)**

```bash
# Start 3 instances on different ports
docker-compose up -d -p 8000
docker-compose up -d -p 8001
docker-compose up -d -p 8002

# Use nginx/reverse-proxy to load balance
```

---

## 📋 Complete Command Reference

| Task                | Command                             |
| ------------------- | ----------------------------------- |
| **Build & Start**   | `docker-compose up --build -d`      |
| **Stop**            | `docker-compose stop`               |
| **Start**           | `docker-compose start`              |
| **Restart**         | `docker-compose restart`            |
| **View Status**     | `docker-compose ps`                 |
| **View Logs**       | `docker-compose logs -f`            |
| **Clean Up**        | `docker-compose down`               |
| **Full Reset**      | `docker-compose down --rmi all -v`  |
| **Enter Container** | `docker-compose exec backend bash`  |
| **Test API**        | `curl http://localhost:8000/health` |

---

## 🎬 Quick Video Walkthrough (Commands)

```bash
# 1. Navigate to Backend
cd Backend

# 2. Start container
docker-compose up --build -d

# 3. Wait 30 seconds for startup

# 4. Check it's running
docker-compose ps

# 5. Test health
curl http://localhost:8000/health

# 6. Open documentation
# http://localhost:8000/docs

# 7. View logs
docker-compose logs -f

# 8. When done, stop
docker-compose stop
```

---

## ✨ What Happens When You Run `docker-compose up --build -d`

```
1. Read docker-compose.yml
2. Build image from Dockerfile (if needed)
   ├─ Download Python 3.11-slim base image
   ├─ Install dependencies from requirements.txt
   ├─ Copy backend code
   ├─ Set up entrypoint
   └─ Tag image as "face-recognition-api"

3. Create container from image
   ├─ Allocate network interface
   ├─ Mount volumes (dataset, models, logs)
   ├─ Set environment variables
   └─ Create isolated environment

4. Start container
   ├─ Run Python FastAPI server
   ├─ Load model on startup
   ├─ Download Firebase images (if available)
   └─ Listen on port 8000

5. Run health check
   ├─ Every 30 seconds
   ├─ Check if API responds to /health
   └─ Update status

6. Container ready! ✅
   ├─ API accessible at http://localhost:8000
   ├─ Logs available via docker-compose logs
   └─ Can stop with docker-compose stop
```

---

## 🚀 Next Steps

After running `docker-compose up --build -d`:

1. ✅ **Verify Running:** `docker-compose ps`
2. ✅ **Check Health:** `curl http://localhost:8000/health`
3. ✅ **View Docs:** Open `http://localhost:8000/docs`
4. ✅ **Test Endpoints:** Try endpoints in Swagger UI
5. ✅ **View Logs:** `docker-compose logs -f`

---

**Ready to run Docker? Just copy and paste:**

```bash
cd Backend && docker-compose up --build -d && echo "✅ Container started! Check http://localhost:8000/health"
```
