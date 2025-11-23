# Llama 3.2 Fine-Tuning Strategy for Forensic Compliance Analysis

## Executive Summary

**Recomendación**: Implementar **LoRA fine-tuning** (Low-Rank Adaptation) con un dataset especializado de ~500-1000 ejemplos de análisis forense de incidentes AI.

**Por qué LoRA**:
- ✅ Eficiente (requiere solo 8-16 GB VRAM vs 80+ GB para full fine-tune)
- ✅ Rápido (3-5 horas vs días para full fine-tune)
- ✅ Portable (guardas solo ~64MB de adaptadores, no 13GB del modelo)
- ✅ Combinable (puedes stacking múltiples LoRAs para diferentes tareas)

---

## Análisis: ¿Qué Necesita Fine-Tuning?

### ¿Qué Llama 3.2 YA HACE BIEN? (No necesita fine-tune)

```
✅ NLP general
✅ Parsing JSON
✅ Classification tasks
✅ Information extraction
✅ Reasoning chains
✅ Code generation
✅ Multi-language support
```

### ¿Qué NECESITA Fine-Tuning? (Específico del dominio)

```
❌ EU AI Act terminology (no está en training data)
❌ Regulatory compliance language
❌ Incident-to-classification mapping
❌ SPARQL query generation
❌ Forensic report writing style
❌ Article 6(3) judgment patterns
❌ Risk assessment language
```

**Diagnóstico**: Llama necesita aprender el **idioma regulatorio específico** de la EU AI Act, no el NLP general.

---

## Approach 1: Zero-Shot (Sin Fine-Tune)

### Cómo Funcionaría

```
System Prompt:
"You are a forensic compliance analyst specialized in EU AI Act violations.
Analyze this AI incident narrative and extract system properties..."

Input:
"Facebook's DeepFace system..."

Output:
{
  "system_type": "facial_recognition",
  "purpose": "content_moderation",
  ...
}
```

### Ventajas
- ✅ Rápido de implementar (hoy mismo)
- ✅ No requiere dataset de training
- ✅ Flexible (puedes cambiar prompts fácilmente)

### Desventajas
- ❌ Inconsistencia en extracciones
- ❌ Hallucinations (inventa información)
- ❌ Formato de output variable
- ❌ Pobre en casos complejos/ambiguos
- ❌ Sin contexto regulatorio

**Confianza esperada**: 65-75%

---

## Approach 2: Few-Shot Prompting (Sin Fine-Tune)

### Cómo Funcionaría

```python
prompt = """
You are a forensic compliance analyst specializing in EU AI Act violations.

EXAMPLES:

Example 1:
Incident: "Amazon's hiring algorithm had gender bias, systematically rejected female candidates"
Extraction:
{
  "system_type": "tabular_classification",
  "purpose": "recruitment",
  "processes": ["employmentData", "personalData"],
  "incident_type": "discrimination",
  "confidence": 0.95
}

Example 2:
Incident: "Clearview AI's facial recognition scraped 3B photos without consent..."
Extraction:
{
  "system_type": "facial_recognition",
  "purpose": "surveillance",
  "processes": ["biometricData", "personalData"],
  "incident_type": "privacy_violation",
  "confidence": 0.94
}

---

NOW analyze this incident:
{USER_INCIDENT_NARRATIVE}
"""
```

### Ventajas
- ✅ Mejor consistencia que zero-shot
- ✅ Más control sobre output format
- ✅ Reduce hallucinations

### Desventajas
- ❌ Token consumption (large prompts)
- ❌ Aún inconsistente en edge cases
- ❌ No aprende realmente, solo imita ejemplos
- ❌ Lento (más tokens = más latencia)

**Confianza esperada**: 75-82%

---

## Approach 3: Full Fine-Tuning (Computacionalmente Costoso)

### Cómo Funcionaría

```
Dataset: 1000 exemplos de:
(incident_narrative, extracted_properties, compliance_assessment)

Training:
- 200 steps
- batch_size: 8
- lr: 2e-5
- epochs: 3
- Duration: 2-3 días en GPU H100

Result: Modelo optimizado específicamente para tu tarea
```

### Ventajas
- ✅ Máxima precisión posible (~90%+)
- ✅ Aprende patrones específicos del dominio
- ✅ Mejor en edge cases
- ✅ Menor latencia en inference

### Desventajas
- ❌ Computacionalmente caro (alquiler GPU: $500-1000)
- ❌ Requiere muchos ejemplos de training
- ❌ Lento de entrenar
- ❌ Modelo final es 13GB (difícil de deployar)
- ❌ No portable (tied a infraestructura específica)
- ❌ Requiere retraining si cambias la ontología

**Confianza esperada**: 88-94%

---

## Approach 4: LoRA Fine-Tuning (RECOMENDADO) ⭐

### Cómo Funcionaría

```
Base Model: Llama 3.2 13B (sin cambios)

LoRA Adapter:
- Rank: 16
- Alpha: 32
- Target modules: q_proj, v_proj, k_proj, o_proj
- Size: ~64MB (vs 13GB del modelo base)

Training:
- Dataset: 500-1000 examples
- Batch size: 16
- Learning rate: 1e-4
- Epochs: 3
- Duration: 1-2 horas en GPU V100
- Cost: ~$10-20

Inference:
- Load base model (cached)
- Load LoRA adapter (~100ms)
- Merge (opcional) o run in parallel
```

### Ventajas
- ✅ Barato y rápido
- ✅ Modelo base sin cambios (reusable)
- ✅ Adapter portátil (~64MB)
- ✅ Puedes combinar múltiples LoRAs
- ✅ Fácil de deployar
- ✅ Recuperable si falla
- ✅ Excelente balance costo/rendimiento

### Desventajas
- ⚠️ Rendimiento ~1-3% inferior a full fine-tune
- ⚠️ Requiere código LoRA compatible

**Confianza esperada**: 85-91%

---

## Recomendación: LoRA Fine-Tuning

### Por qué LoRA es óptimo para este caso de uso

**1. Dataset Size**: Tienes ~500-1000 incidentes en AIAAIC
- ✅ Perfecto para LoRA (necesita menos que full fine-tune)
- ❌ Marginal para full fine-tune (quieren 10K+)

**2. Domain Specificity**: Necesitas capturar lenguaje regulatorio
- ✅ LoRA aprende patrones de dominio eficientemente
- ✅ No necesita fuerza bruta de full fine-tune

**3. Deployment**: Sistema de enforcement en producción
- ✅ LoRA adapter cabe en cualquier servidor
- ✅ Full fine-tune requiere GPU costosa

**4. Flexibility**: Regulaciones evolucionan constantemente
- ✅ Reentrenar LoRA es barato (reutiliza base)
- ❌ Full fine-tune requiere GPU nuevamente

---

## Implementación: LoRA Fine-Tuning

### Step 1: Preparar Dataset

```python
# Dataset structure for LoRA training

training_data = [
    {
        "incident_id": "AIAAIC-2015-FB-01",
        "narrative": "Facebook's DeepFace system...",
        "extraction": {
            "system_name": "Facebook DeepFace",
            "system_type": "facial_recognition",
            "primary_purpose": "image_tagging",
            "processes": ["BiometricData", "PersonalData"],
            "deployment_context": ["PublicSpaces", "HighVolume"],
            "incident_type": "discrimination",
            "affected_populations": ["Black users", "Minorities"],
            "confidence": 0.95
        },
        "classification": {
            "proper_risk_level": "HighRisk",
            "mandatory_requirements": [
                "BiometricSecurityRequirement",
                "FundamentalRightsAssessmentRequirement",
                ...
            ]
        },
        "gaps": {
            "missing": ["BiasDetectionRequirement", ...],
            "missing_count": 5,
            "compliance_ratio": 0.29
        }
    },
    # ... 499 more examples
]

# Convert to JSONL for training
with open("training_data.jsonl", "w") as f:
    for example in training_data:
        f.write(json.dumps(example) + "\n")
```

### Step 2: Define Training Task

```python
# What patterns should Llama learn?

SYSTEM_PROMPT = """You are a forensic EU AI Act compliance analyst.

Given an AI incident narrative, you must:
1. Extract system properties (type, purpose, data types, deployment)
2. Classify the incident type (discrimination, safety, privacy, etc.)
3. Assess confidence in each extraction

OUTPUT MUST BE VALID JSON.
"""

TRAINING_EXAMPLES = [
    {
        "input": narrative,
        "output": json.dumps({
            "system": extraction["system"],
            "incident": extraction["incident_type"],
            "confidence": extraction["confidence"],
            "affected_populations": extraction["affected_populations"]
        })
    }
    for narrative, extraction in training_data
]
```

### Step 3: LoRA Configuration

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load base model (unmodified)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-13b-hf",
    device_map="auto",
    torch_dtype=torch.float16
)

# Configure LoRA
lora_config = LoraConfig(
    r=16,                          # Rank of adaptation
    lora_alpha=32,                 # Scaling factor
    target_modules=[
        "q_proj",                  # Query projection
        "v_proj",                  # Value projection
        "k_proj",                  # Key projection
        "o_proj"                   # Output projection
    ],
    lora_dropout=0.05,             # Dropout for regularization
    bias="none",                   # No bias adaptation
    task_type="CAUSAL_LM"          # Task type
)

# Create PEFT model
model = get_peft_model(model, lora_config)

# Check trainable params
trainable_params = sum(
    p.numel() for p in model.parameters() if p.requires_grad
)
total_params = sum(p.numel() for p in model.parameters())

print(f"Trainable: {trainable_params:,} ({100*trainable_params/total_params:.1f}%)")
# Output: Trainable: 4,194,304 (0.6% of 6.7B total)
```

### Step 4: Training Configuration

```python
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./forensic-lora-checkpoint",

    # Training parameters
    num_train_epochs=3,
    per_device_train_batch_size=16,
    gradient_accumulation_steps=1,
    optim="paged_adamw_32bit",     # Memory efficient optimizer

    # Learning rate
    learning_rate=1e-4,
    warmup_steps=100,
    weight_decay=0.01,

    # Logging and saving
    logging_steps=10,
    save_steps=100,
    save_total_limit=3,

    # Validation
    evaluation_strategy="steps",
    eval_steps=100,

    # Hardware
    fp16=True,                      # Mixed precision (16-bit)
    gradient_checkpointing=True,    # Save memory
    max_grad_norm=1.0,

    # Generation
    max_length=512,

    # Output
    report_to="wandb",              # Log to W&B
    push_to_hub=True,
    hub_model_id="your-org/forensic-llama-lora"
)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    data_collator=data_collator,
    callbacks=[EarlyStoppingCallback()]
)

# Start training
trainer.train()
```

### Step 5: Inference with LoRA

```python
from peft import AutoPeftModelForCausalLM

# Load base model with LoRA adapter
model = AutoPeftModelForCausalLM.from_pretrained(
    "your-org/forensic-llama-lora"
)

# Optional: merge LoRA into base (creates standalone model)
merged_model = model.merge_and_unload()

# Use for inference
def analyze_incident(narrative: str) -> dict:
    prompt = f"""Analyze this AI incident and extract compliance information:

    INCIDENT: {narrative}

    EXTRACTION (JSON):"""

    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=512, temperature=0.3)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return json.loads(response.split("EXTRACTION (JSON):")[1])
```

---

## Dataset Composition (Critical!)

### Size Recommendations

| Scenario | Dataset Size | Fine-Tune Method | Time | Cost |
|----------|--------------|------------------|------|------|
| MVP/PoC | 100-200 | LoRA (r=8) | 30min | $2-5 |
| Good performance | 500-800 | LoRA (r=16) | 1-2h | $10-20 |
| Production | 1000-2000 | LoRA (r=32) | 2-4h | $20-40 |
| Excellent | 5000+ | Full fine-tune | 2-3 days | $500+ |

**Recomendación**: Empieza con 500 ejemplos y LoRA r=16

### Data Quality Requirements

```python
# What makes a good training example?

good_example = {
    "incident": "Clear narrative with system description, harm type, timeline",
    "extraction": "Accurate, complete, consistent with EU AI Act terminology",
    "classification": "Correct risk level, requirements, gaps identified",
    "confidence": "Reflects actual correctness of extraction"
}

bad_example = {
    "incident": "Vague or incomplete narrative",
    "extraction": "Hallucinated or incorrect information",
    "classification": "Inconsistent or missing critical details",
    "confidence": "Inflated or unrealistic"
}

# Data validation checklist
- ✅ All extractions are JSON-valid
- ✅ All system types exist in ontology
- ✅ All incident types are recognized
- ✅ Confidence scores are 0.7+ (don't train on low-confidence)
- ✅ Classifications match ontology requirements
- ✅ No duplicates or near-duplicates
- ✅ No PII in narratives
```

---

## Dataset Construction Workflow

### Option A: Manual Curation (Recommended for v1)

```
1. Select 50-100 best-documented AIAAIC incidents
2. Have expert manually extract properties
3. Verify extractions match ontology
4. Use as "gold standard" training set
5. Cost: $2000-3000 (expert labor)
6. Time: 2-4 weeks
7. Quality: Excellent ⭐⭐⭐⭐⭐
```

### Option B: Semi-Automated + Expert Review

```
1. Use zero-shot Llama to generate extractions
2. Expert reviews + corrects extractions
3. Keep only high-confidence examples (>0.85)
4. Iterate until 500 examples
5. Cost: $1000-1500 (less expert labor)
6. Time: 1-2 weeks
7. Quality: Good ⭐⭐⭐⭐
```

### Option C: Synthetic Data Generation

```
1. Template-based generation:
   - Combine system types + purposes + contexts
   - Generate realistic narratives
   - Add variations (4-5 per template)

2. Would give 1000+ examples quickly
3. Cost: Low ($100-300 for curation)
4. Time: 1 week
5. Quality: Medium ⭐⭐⭐
6. Risk: Data distribution drift
```

**Recomendación**: Combinar A + B (manual core + semi-automated expansion)

---

## Training Phases

### Phase 1: PoC (2 semanas)
- Dataset: 100-150 manually curated examples
- LoRA: r=8, alpha=16
- Time: 30 min training
- Validation: Test on 10 unseen incidents
- Cost: ~$5

### Phase 2: Production (6 semanas)
- Dataset: 500-800 examples (A+B mix)
- LoRA: r=16, alpha=32
- Time: 1-2 hours training
- Validation: Benchmark against expert
- Cost: ~$15-20

### Phase 3: Excellence (12+ weeks)
- Dataset: 1000+ examples
- Consider full fine-tune vs multi-LoRA
- Validation: Production metrics tracking
- Cost: Variable based on scaling

---

## Evaluation Metrics

```python
# How to measure if fine-tuning is working?

def evaluate_extraction(predicted, gold_standard):
    """
    Compare predicted extraction vs ground truth
    """

    metrics = {
        # Exact match
        "exact_match": predicted == gold_standard,

        # Partial match (key properties)
        "system_type_match": (
            predicted["system"]["type"] ==
            gold_standard["system"]["type"]
        ),

        # Classification accuracy
        "incident_type_match": (
            predicted["incident"]["type"] ==
            gold_standard["incident"]["type"]
        ),

        # Confidence calibration
        "confidence_score": abs(
            predicted["confidence"] -
            gold_standard["confidence"]
        ),

        # JSON validity
        "json_valid": is_valid_json(predicted),

        # Ontology alignment
        "ontology_valid": all(
            req in ontology.requirements
            for req in predicted["requirements"]
        )
    }

    return metrics

# Aggregate metrics
def compute_metrics(predictions, gold_standards):
    results = {
        "exact_match_rate": 0.0,      # Target: >80%
        "system_type_accuracy": 0.0,  # Target: >92%
        "incident_type_accuracy": 0.0, # Target: >90%
        "avg_confidence_error": 0.0,  # Target: <0.10
        "json_validity": 0.0,         # Target: 100%
        "ontology_alignment": 0.0     # Target: 100%
    }

    for pred, gold in zip(predictions, gold_standards):
        metrics = evaluate_extraction(pred, gold)
        # Aggregate...

    return results
```

---

## Implementation Roadmap

```
Week 1-2: Data Preparation
├─ Collect 50 best AIAAIC incidents
├─ Manual extraction + verification
├─ Create JSONL training file
└─ Split train/val (80/20)

Week 3: PoC Training
├─ Setup LoRA environment
├─ Train on 100-150 examples
├─ Evaluate on 20 holdout incidents
└─ Decision: Continue or iterate?

Week 4-6: Production Training
├─ Expand dataset to 500+ examples
├─ Semi-automated generation + expert review
├─ Retrain LoRA with r=16
├─ Benchmark vs zero-shot
└─ Deploy to staging

Week 7+: Optimization
├─ Monitor performance in production
├─ Collect failure cases
├─ Retrain periodically
└─ Consider full fine-tune if needed
```

---

## Cost Comparison

```
Method                  Initial Cost    Training Time    Inference    Portability
────────────────────────────────────────────────────────────────────────────────
Zero-shot (no tune)     $0              N/A              Fast         N/A
Few-shot (no tune)      $0              N/A              Slower       N/A
LoRA PoC (r=8)         $5              30 min           ~1ms          ✅ Easy
LoRA Prod (r=16)       $15-20          1-2h             ~2ms          ✅ Easy
LoRA+ (r=32)           $30-50          3-4h             ~3ms          ✅ Easy
Full Fine-tune         $500-1000       2-3 days         ~1ms          ❌ Hard
Serve Multiple LoRAs   $20-30          1-2h each        ~4ms          ✅ Very easy
────────────────────────────────────────────────────────────────────────────────

Best Value: LoRA Prod (r=16)
- Cost: $20
- Quality gain vs zero-shot: +15-20%
- Inference quality: Excellent
- Maintainability: Excellent
```

---

## Why LoRA Over Alternatives?

### vs Zero-Shot
```
Zero-shot:  Speed ⭐⭐⭐⭐⭐ | Quality ⭐⭐⭐ | Cost $0
LoRA:       Speed ⭐⭐⭐⭐   | Quality ⭐⭐⭐⭐⭐ | Cost $20

Winner: LoRA (20% better quality for $20)
```

### vs Full Fine-Tune
```
Full:       Speed ⭐ | Quality ⭐⭐⭐⭐⭐ | Cost $1000
LoRA:       Speed ⭐⭐⭐⭐⭐ | Quality ⭐⭐⭐⭐ | Cost $20

Winner: LoRA (95% quality at 2% cost)
```

### vs Prompt Engineering
```
Few-shot:   Maintainability ❌ | Performance ⭐⭐⭐⭐ | Cost $0
LoRA:       Maintainability ✅ | Performance ⭐⭐⭐⭐⭐ | Cost $20

Winner: LoRA (better performance + cleaner code)
```

---

## Final Recommendation

**Implementar LoRA Fine-Tuning con esta secuencia**:

```
1. Weeks 1-2: Curate 150-200 manual examples
   → Cost: $2000-3000 (expert)
   → Quality: Perfect baseline

2. Week 3: Train LoRA PoC (r=8, 100 examples)
   → Cost: $5
   → Result: Validate approach works

3. Weeks 4-6: Expand to 500-800 examples
   → Semi-automated + expert review
   → Cost: $1000 (reduced expert labor)
   → Train LoRA production (r=16)
   → Cost: $20

4. Weeks 7+: Production deployment
   → Monitor performance
   → Retrain quarterly with new incidents
   → Cost: $20/quarter

TOTAL YEAR 1: ~$4,000
TOTAL YEAR 2+: ~$100/year (just retraining)
```

**This is the optimal balance of:**
- ✅ Cost-effectiveness
- ✅ Fast to implement
- ✅ High quality
- ✅ Easy to maintain
- ✅ Scalable approach

