# 🧪 Ejemplos CURL - Probar SHACL Validation

## Requisitos Previos

```bash
# 1. Backend ejecutando
docker-compose up backend

# 2. Razonador ejecutando
docker-compose up reasoner

# 3. (Opcional) Instalar pyshacl
pip install pyshacl
```

---

## Test 1: Verificar Estado SHACL

```bash
curl -X GET "http://localhost:8000/reasoning/shacl/status" \
  -H "Content-Type: application/json"
```

**Respuesta esperada:**

```json
{
  "shacl_validation": {
    "enabled": true,
    "available": true,
    "shapes_path": "/ontologias/shacl/ai-act-shapes.ttl",
    "shapes_file_exists": true,
    "status": "active"
  }
}
```

---

## Test 2: Validar Sistema Válido (Pre-Validation)

```bash
curl -X POST "http://localhost:8000/reasoning/validate-system" \
  -H "Content-Type: application/json" \
  -d '{
    "hasName": "Healthcare AI System",
    "hasPurpose": ["HealthCare"],
    "hasDeploymentContext": ["HighVolumeProcessing"],
    "hasTrainingDataOrigin": ["PublicData"],
    "hasVersion": "1.0.0"
  }'
```

**Respuesta esperada:**

```json
{
  "valid": true,
  "message": "Sistema válido",
  "shacl_enabled": true,
  "ttl_preview": "@prefix ai: <http://ai-act.eu/ai#> .\n..."
}
```

---

## Test 3: Validar Sistema Incompleto (PRE-Validation FALLA)

```bash
curl -X POST "http://localhost:8000/reasoning/validate-system" \
  -H "Content-Type: application/json" \
  -d '{
    "hasName": "Incomplete System"
    # ❌ SIN hasPurpose
    # ❌ SIN hasDeploymentContext
    # ❌ SIN hasTrainingDataOrigin
  }'
```

**Respuesta esperada:**

```json
{
  "valid": false,
  "message": "Sistema incumple restricciones pre-razonamiento:\nConforms: false\n\nIntelligentSystem must have at least one hasPurpose...",
  "shacl_enabled": true,
  "ttl_preview": "@prefix ai: <http://ai-act.eu/ai#> .\n..."
}
```

---

## Test 4: Razonamiento CON Validación SHACL

### Paso 1: Crear sistema en BD

```bash
# Crear un sistema de ejemplo
curl -X POST "http://localhost:8000/systems/create" \
  -H "Content-Type: application/json" \
  -d '{
    "hasName": "Recruitment AI - Test SHACL",
    "hasPurpose": ["RecruitmentOrEmployment"],
    "hasDeploymentContext": ["HighVolumeProcessing"],
    "hasTrainingDataOrigin": ["PublicData"],
    "hasVersion": "2.0.0"
  }'

# Respuesta (guardar el _id):
# {
#   "_id": "507f1f77bcf86cd799439011",
#   "hasName": "Recruitment AI - Test SHACL",
#   ...
# }
```

### Paso 2: Ejecutar razonamiento CON validación

```bash
curl -X POST "http://localhost:8000/reasoning/system/507f1f77bcf86cd799439011" \
  -H "Content-Type: application/json"
```

**Respuesta esperada (CON validación SHACL):**

```json
{
  "system_id": "507f1f77bcf86cd799439011",
  "system_name": "Recruitment AI - Test SHACL",
  "reasoning_completed": true,
  "inferred_relationships": {
    "hasNormativeCriterion": [
      "http://ai-act.eu/ai#NonDiscrimination"
    ],
    "hasTechnicalCriterion": [
      "http://ai-act.eu/ai#ScalabilityRequirements"
    ],
    "hasContextualCriterion": [],
    "hasRequirement": [],
    "hasTechnicalRequirement": []
  },
  "raw_ttl": "@prefix ai: <http://ai-act.eu/ai#> ...",
  "rules_applied": 2,
  "shacl_validation": {
    "pre_validation": {
      "status": "passed",
      "enabled": true
    },
    "post_validation": {
      "status": "passed",
      "valid": true,
      "message": "Válido",
      "enabled": true
    }
  }
}
```

---

## Test 5: Ver Logs de Validación

```bash
# Ver logs de validación
docker logs -f <backend-container> | grep -i "shacl\|validation"
```

**Logs esperados:**

```
[INFO] Iniciando pre-validación SHACL...
[INFO] Pre-validation passed
[INFO] Iniciando post-validación SHACL...
[INFO] Post-validación completada: Válido
```

---

## Test 6: Deshabilitar SHACL (Opcional)

```bash
# Configurar para deshabilitar SHACL
export ENABLE_SHACL_VALIDATION=false

# Reiniciar backend
docker-compose restart backend

# Verificar estado
curl -X GET "http://localhost:8000/reasoning/shacl/status"

# Respuesta:
# {
#   "shacl_validation": {
#     "enabled": false,
#     "available": true,
#     "status": "disabled"
#   }
# }
```

---

## Test 7: Sin pyshacl Instalado

Si `pyshacl` no está instalado:

```bash
curl -X GET "http://localhost:8000/reasoning/shacl/status"

# Respuesta:
# {
#   "shacl_validation": {
#     "enabled": true,
#     "available": false,    ← ⚠️ Graceful degradation
#     "status": "disabled"
#   }
# }
```

Backend sigue funcionando sin errores.

---

## Test Batch: Script de Prueba

```bash
#!/bin/bash

echo "=== Test 1: Estado SHACL ==="
curl -s http://localhost:8000/reasoning/shacl/status | jq .

echo -e "\n=== Test 2: Validar Sistema Válido ==="
curl -s -X POST http://localhost:8000/reasoning/validate-system \
  -H "Content-Type: application/json" \
  -d '{
    "hasName": "Test Valid",
    "hasPurpose": ["HealthCare"],
    "hasDeploymentContext": ["HighVolumeProcessing"],
    "hasTrainingDataOrigin": ["PublicData"]
  }' | jq .

echo -e "\n=== Test 3: Validar Sistema Inválido ==="
curl -s -X POST http://localhost:8000/reasoning/validate-system \
  -H "Content-Type: application/json" \
  -d '{"hasName": "Incomplete"}' | jq .

echo -e "\n=== Todos los tests completados ==="
```

---

## Test de Rendimiento

### Medir tiempo de validación SHACL

```bash
# Time para validación (sin razonamiento)
time curl -X POST "http://localhost:8000/reasoning/validate-system" \
  -H "Content-Type: application/json" \
  -d '{
    "hasName": "Performance Test",
    "hasPurpose": ["HealthCare"],
    "hasDeploymentContext": ["HighVolumeProcessing"],
    "hasTrainingDataOrigin": ["PublicData"]
  }' > /dev/null

# Tiempo esperado: < 100ms
```

### Medir impacto en razonamiento

```bash
# Time para razonamiento CON validación SHACL
time curl -X POST "http://localhost:8000/reasoning/system/{system_id}"

# Tiempo esperado:
#   - Pre-validation: < 100ms
#   - Razonamiento: variable (depende de Jena)
#   - Post-validation: < 100ms
#   - Total: < 3s típicamente
```

---

## Troubleshooting

### Error: "pyshacl not installed"

```bash
# Solución: Instalar pyshacl
pip install pyshacl

# O en Docker:
# RUN pip install pyshacl
```

### Error: "SHACL shapes file not found"

```bash
# Verificar ruta
ls -la /ontologias/shacl/ai-act-shapes.ttl

# O ajustar variable de ambiente
export SHACL_SHAPES_PATH="/ruta/correcta/ai-act-shapes.ttl"
```

### Error: "Sistema incumple restricciones"

```bash
# Ver detalles en respuesta
curl -s -X POST http://localhost:8000/reasoning/validate-system \
  -H "Content-Type: application/json" \
  -d '...' | jq .message

# Buscar en logs:
docker logs <container> | grep "Violation Details"
```

---

## Tabla de Respuestas Esperadas

| Test | Endpoint | Status | Validación |
|------|----------|--------|------------|
| **1** | `/shacl/status` | 200 | N/A |
| **2** | `/validate-system` (válido) | 200 | valid: true |
| **3** | `/validate-system` (inválido) | 200 | valid: false |
| **4** | `/system/{id}` | 200 | pre_validation passed, post_validation passed |
| **5** | Logs | - | SHACL: validation (pre/post) |
| **6** | `/shacl/status` (disabled) | 200 | enabled: false |
| **7** | `/shacl/status` (no pyshacl) | 200 | available: false |

---

## Scripts para Automatizar Tests

### Python Test Script

```python
import requests
import json

BASE_URL = "http://localhost:8000/reasoning"

def test_shacl_status():
    """Test 1: Verificar estado SHACL"""
    response = requests.get(f"{BASE_URL}/shacl/status")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_valid_system():
    """Test 2: Sistema válido"""
    data = {
        "hasName": "Valid Test",
        "hasPurpose": ["HealthCare"],
        "hasDeploymentContext": ["HighVolumeProcessing"],
        "hasTrainingDataOrigin": ["PublicData"]
    }
    response = requests.post(f"{BASE_URL}/validate-system", json=data)
    print(f"Valid system test: {response.json()['valid']}")

def test_invalid_system():
    """Test 3: Sistema inválido"""
    data = {"hasName": "Incomplete"}
    response = requests.post(f"{BASE_URL}/validate-system", json=data)
    print(f"Invalid system test: {response.json()['valid']}")

if __name__ == "__main__":
    print("=== Test 1 ===")
    test_shacl_status()
    print("\n=== Test 2 ===")
    test_valid_system()
    print("\n=== Test 3 ===")
    test_invalid_system()
```

---

**Generado:** 22 Nov 2025
**Ejemplos CURL para SHACL Validation**
**Versión:** reasoning.py v2.0
