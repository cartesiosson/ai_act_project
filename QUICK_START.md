# 🚀 Quick Start Guide - SHACL Integration

**Last Updated:** 22 Nov 2025
**Time to Deploy:** ~5 minutes

---

## ⚡ Deploy in 5 Minutes

```bash
# 1. Build Docker images (2 min)
cd /home/cartesio/workspace/ai_act_public/ai_act_project
docker-compose build backend reasoner_service

# 2. Start services (1 min)
docker-compose up -d

# 3. Verify services are healthy (30 sec)
docker-compose ps
# Should show: STATUS: Up X seconds (healthy)

# 4. Test SHACL is working (30 sec)
curl http://localhost:8000/reasoning/shacl/status

# Expected response:
# {
#   "shacl_validation": {
#     "enabled": true,
#     "available": true,
#     "status": "active"
#   }
# }
```

That's it! You're ready to go.

---

## 📋 What Changed

### Files Modified
- `backend/requirements.txt` - Added `pyshacl`
- `backend/Dockerfile` - Added HEALTHCHECK, logging, documentation
- `reasoner_service/Dockerfile` - Added HEALTHCHECK, logging, documentation
- `backend/routers/reasoning.py` - Added SHACL validation

### What You Get
- ✅ Pre-validation of systems before reasoning (blocks invalid systems)
- ✅ Post-validation of reasoning results (reports on quality)
- ✅ HEALTHCHECK on both services (visible in `docker ps`)
- ✅ Better logging and monitoring (INFO level)
- ✅ Complete documentation (11 files)

---

## 🧪 Quick Tests

### Test 1: Check SHACL Status
```bash
curl http://localhost:8000/reasoning/shacl/status
```

### Test 2: Pre-validate a System (Valid)
```bash
curl -X POST http://localhost:8000/reasoning/validate-system \
  -H "Content-Type: application/json" \
  -d '{
    "hasName": "Test System",
    "hasPurpose": ["HealthCare"],
    "hasDeploymentContext": ["HighVolumeProcessing"],
    "hasTrainingDataOrigin": ["PublicData"]
  }'
```

### Test 3: Pre-validate a System (Invalid)
```bash
curl -X POST http://localhost:8000/reasoning/validate-system \
  -H "Content-Type: application/json" \
  -d '{"hasName": "Incomplete"}'
# Should return: HTTP 200 with valid: false
```

### Test 4: Check Docker Health
```bash
docker-compose ps
# Look for: STATUS column showing "(healthy)"
```

For more tests, see [EJEMPLOS_SHACL_CURL.md](EJEMPLOS_SHACL_CURL.md).

---

## 📚 Documentation

### Read First
1. **[SESSION_SUMMARY.md](SESSION_SUMMARY.md)** - 5 min read, overview of everything
2. **[COMPLETION_REPORT.md](COMPLETION_REPORT.md)** - This session's status

### Before Deploying
- **[DOCKER_IMPROVEMENTS_COMPLETE.md](DOCKER_IMPROVEMENTS_COMPLETE.md)** - Docker configuration
- **[ACTUALIZACION_DOCKER_SHACL.md](ACTUALIZACION_DOCKER_SHACL.md)** - Deployment steps

### Testing
- **[EJEMPLOS_SHACL_CURL.md](EJEMPLOS_SHACL_CURL.md)** - 7 test examples

### Understanding the System
- **[ARCHITECTURE_SHACL.md](ARCHITECTURE_SHACL.md)** - System design
- **[IMPLEMENTACION_SHACL_EN_REASONING.md](IMPLEMENTACION_SHACL_EN_REASONING.md)** - Code details
- **[SHACL_EXPLICACION_DETALLADA.md](SHACL_EXPLICACION_DETALLADA.md)** - SHACL concepts
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Navigation guide

---

## 🔧 Common Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View service status
docker-compose ps

# View logs (all services)
docker-compose logs

# View logs (backend only)
docker-compose logs backend

# View logs (real-time)
docker-compose logs -f

# Rebuild images
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Rebuild specific service
docker-compose build backend

# Test API
curl http://localhost:8000/reasoning/shacl/status

# View ontology version
docker-compose exec reasoner python -c "import os; print(os.environ.get('CURRENT_RELEASE'))"
```

---

## ⚙️ Configuration

### Environment Variables

Set these to customize behavior:

```bash
# Enable/disable SHACL validation
ENABLE_SHACL_VALIDATION=true  # true or false

# Path to SHACL shapes file
SHACL_SHAPES_PATH=/ontologias/shacl/ai-act-shapes.ttl

# Path to ontology file
ONTOLOGY_PATH=/ontologias/versions/0.37.1/ontologia-v0.37.1.ttl
```

To set them:
```bash
# In docker-compose.yml, under backend service:
environment:
  - ENABLE_SHACL_VALIDATION=true
  - SHACL_SHAPES_PATH=/ontologias/shacl/ai-act-shapes.ttl
  - ONTOLOGY_PATH=/ontologias/versions/0.37.1/ontologia-v0.37.1.ttl
```

---

## 🚨 Troubleshooting

### "UNHEALTHY status in docker ps"
```bash
# Check logs
docker-compose logs backend

# Verify the endpoint exists
curl http://localhost:8000/reasoning/status

# Restart service
docker-compose restart backend
```

### "pyshacl not found error"
```bash
# Rebuild backend image
docker-compose build --no-cache backend

# Verify installation
docker-compose exec backend pip list | grep pyshacl

# Should show: pyshacl (some version)
```

### "Connection refused"
```bash
# Check if services are running
docker-compose ps

# If not running, start them
docker-compose up -d

# If running but not responding, check logs
docker-compose logs backend | tail -20
```

### "Port 8000 already in use"
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port in docker-compose.yml
```

---

## ✅ Verification Checklist

After deploying:

```
□ docker-compose ps shows all services as HEALTHY
□ curl http://localhost:8000/reasoning/shacl/status returns 200 OK
□ Test 1 (valid system) returns valid: true
□ Test 2 (invalid system) returns valid: false
□ docker-compose logs shows no ERROR messages
□ SHACL validation is working correctly
```

---

## 🔄 Update to Latest

If you need to update later:

```bash
# Pull latest changes
git pull origin refine

# Rebuild Docker images
docker-compose build

# Restart services
docker-compose up -d

# Verify
docker-compose ps
```

---

## 📞 Need Help?

- **Deploying:** See [DOCKER_IMPROVEMENTS_COMPLETE.md](DOCKER_IMPROVEMENTS_COMPLETE.md)
- **Testing:** See [EJEMPLOS_SHACL_CURL.md](EJEMPLOS_SHACL_CURL.md)
- **Understanding:** See [ARCHITECTURE_SHACL.md](ARCHITECTURE_SHACL.md)
- **Code:** See [IMPLEMENTACION_SHACL_EN_REASONING.md](IMPLEMENTACION_SHACL_EN_REASONING.md)
- **Navigation:** See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

## 🎯 Next Steps

1. ✅ Deploy: Run the 5-minute deployment above
2. ✅ Test: Run the quick tests above
3. ✅ Verify: Check the verification checklist
4. ✅ Learn: Read the documentation files (start with SESSION_SUMMARY.md)
5. ✅ Deploy to production: Follow [ACTUALIZACION_DOCKER_SHACL.md](ACTUALIZACION_DOCKER_SHACL.md)

---

## 🎉 You're Done!

The system is ready to use. SHACL validation is working and all services are monitored.

**Status:** Production Ready ✅

---

**Last Updated:** 22 Nov 2025
**Time to Deploy:** ~5 minutes
**Difficulty:** Easy (just follow the steps above)
