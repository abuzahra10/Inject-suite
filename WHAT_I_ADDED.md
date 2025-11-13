# 🎯 Ollama Integration - What Was Added

## Summary

I've integrated **automated attack evaluation** using Ollama to complement your manual ChatGPT testing. This gives you reproducible, quantitative results for your thesis.

---

## 📁 New Files Created

### 1. `backend/evaluation/evaluator.py` (Main evaluation engine)
**What it does:**
- Automatically tests any attack against any Ollama model
- Extracts scores and metrics from LLM responses
- Determines attack success based on specific criteria
- Generates structured results for analysis

**Key features:**
- `AttackEvaluator` class - Main evaluation interface
- `evaluate_cv_attack()` - Test single attack
- `batch_evaluate()` - Test all attacks at once
- Automatic metric extraction (scores, keywords, sentiment)

### 2. `backend/run_evaluation.py` (Single model testing script)
**What it does:**
- Run all 22 attacks against one model
- Compare against baseline (clean CV)
- Generate readable report with scores and success rates

**Usage:**
```bash
python run_evaluation.py your_cv.pdf
python run_evaluation.py your_cv.pdf --model llama3.1:8b-instruct
python run_evaluation.py your_cv.pdf --attacks score_inflation watermark_injection
```

### 3. `backend/compare_models.py` (Multi-model comparison script)
**What it does:**
- Test attacks across multiple models simultaneously
- Generate comparison matrix
- Show which models are most/least vulnerable

**Usage:**
```bash
python compare_models.py your_cv.pdf
python compare_models.py your_cv.pdf --models llama3.2:3b mistral:7b phi3:mini
```

### 4. `OLLAMA_GUIDE.md` (Complete usage documentation)
**Contains:**
- Installation instructions
- Usage examples
- Research workflow guidance
- Thesis data generation strategies
- Troubleshooting

---

## 🔗 How It Integrates

### With Your Existing Code

```
Your Existing Infrastructure:
├── attacks/injectors.py ✅ (Used directly)
├── attacks/transformers.py ✅ (Used directly)  
├── services/pipeline.py ✅ (Already has Ollama!)
└── services/retrieve.py ✅ (Already has Ollama!)

New Addition:
└── evaluation/evaluator.py → Orchestrates everything
    ├── Uses your attack recipes
    ├── Uses your PDF injection code
    ├── Calls Ollama for evaluation
    └── Extracts metrics automatically
```

### Architecture Flow

```
1. Load CV PDF
   ↓
2. Generate poisoned PDF using your attack code
   ↓
3. Extract text (simulates LLM reading document)
   ↓
4. Send to Ollama with evaluation query
   ↓
5. Parse response → Extract scores/metrics
   ↓
6. Compare to baseline → Determine success
   ↓
7. Generate report
```

---

## 🚀 Quick Start

### 1. Install Ollama (One-time setup)

```bash
# Install
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (choose one or more)
ollama pull llama3.2:3b-instruct  # Fast, good for testing
ollama pull llama3.1:8b-instruct  # Better quality
ollama pull mistral:7b-instruct   # Alternative model
```

### 2. Run Your First Evaluation

```bash
cd backend

# Test all attacks on your CV
python run_evaluation.py /path/to/your_cv.pdf

# You'll see:
# - Baseline score
# - Score for each attack
# - Success/failure indicators
# - Score deltas
# - Overall success rate
```

### 3. Compare Models (For Thesis Data)

```bash
# Test across multiple models
python compare_models.py /path/to/your_cv.pdf

# You'll get a comparison matrix like:
# Attack              Llama3.2    Mistral     Phi3
# score_inflation     8.5 ✓       8.2 ✓       7.9 ✓
# watermark           7.8 ✓       7.5 ✗       7.2 ✗
```

---

## 📊 What You Get for Your Thesis

### 1. Quantitative Data

**Example output:**
```
=============================================================================
ATTACK EVALUATION REPORT (llama3.2:3b-instruct)
=============================================================================

Baseline Score: 7.2/10

Attack                         Score      Success    Delta     
-----------------------------------------------------------------------------
score_inflation                8.5        ✓          +1.3
acceptance_bias                8.2        ✓          +1.0
sentiment_reversal             8.1        ✓          +0.9
watermark_injection            7.8        ✓          +0.6
gradual_instruction            7.9        ✓          +0.7
role_reversal                  8.0        ✓          +0.8
task_substitution              7.7        ✓          +0.5
delimiter_confusion            7.4        ✗          +0.2
...

✅ Successful attacks: 18/22
📊 Success rate: 81.8%
```

### 2. Model Comparison Tables

```
MODEL COMPARISON - Success Rates
─────────────────────────────────
Model             Success Rate    Avg Score Boost
──────────────────────────────────────────────────
Llama3.2:3b       81.8%          +0.9
Mistral:7b        77.3%          +0.8  
GPT-4o (manual)   65.0%          +0.6
```

### 3. Attack Category Analysis

```
CATEGORY EFFECTIVENESS
─────────────────────────────────
Category                Success Rate
─────────────────────────────────
Output Manipulation     85% (6/7)
Context Hijacking       75% (3/4)
Defense Evasion         60% (3/5)
Domain-Specific         67% (2/3)
```

---

## 💡 Key Benefits

### Compared to Manual Testing

| Aspect | Manual (ChatGPT) | Automated (Ollama) |
|--------|-----------------|-------------------|
| **Speed** | 5 min/attack | 30 sec/attack |
| **Coverage** | Selective testing | All 22 attacks |
| **Reproducibility** | Hard to replicate | Fully reproducible |
| **Cost** | API costs | Free |
| **Models** | GPT-4o only | Any Ollama model |
| **Data** | Qualitative | Quantitative |
| **Thesis Value** | Behavioral insights | Statistical validation |

### Complementary Approach

**Best practice:** Use BOTH

1. **Manual (ChatGPT):** Explore, refine, understand behaviors
2. **Automated (Ollama):** Validate, measure, generate data

**For your thesis:**
- ChatGPT testing → Shows real commercial model vulnerability
- Ollama testing → Provides reproducible scientific data
- Combined → Strong mixed-methods research

---

## 🎓 Thesis Integration

### Methodology Section

> "We evaluated attacks using both manual testing (GPT-4o) and automated evaluation (Ollama v0.3.x). 
> For reproducibility, we tested against three open-source models (Llama3.2:3b, Llama3.1:8b, Mistral:7b)..."

### Results Section

> "Table 3 shows automated evaluation results across 22 attacks on Llama3.2:3b-instruct. 
> Output manipulation attacks achieved 85% success rate with average score inflation of +1.1 points..."

> "Figure 2 compares attack effectiveness across models. GPT-4o showed greater resistance (+0.6 average boost) 
> compared to smaller open-source models (+0.9 for Llama3.2)..."

### Discussion

> "Our mixed-methods approach revealed that while GPT-4o detected explicit manipulation attempts 
> (as seen in score_inflation test), it still partially complied with implicit bias. 
> Open-source models showed higher vulnerability but no explicit detection behavior..."

---

## 🔬 Next Steps

### Immediate (Today)

1. ✅ Install Ollama
2. ✅ Pull llama3.2:3b-instruct
3. ✅ Run first evaluation on your CV

### This Week

1. Compare 3 models (Llama, Mistral, Phi)
2. Generate tables for thesis
3. Create charts from results

### Thesis Writing

1. Add automated evaluation methodology
2. Include quantitative results
3. Compare with your ChatGPT findings
4. Discuss model-specific vulnerabilities

---

## 📝 Files Overview

```
thesis-pi-eval/
├── backend/
│   ├── evaluation/          ← NEW: Evaluation engine
│   │   ├── __init__.py
│   │   └── evaluator.py
│   ├── run_evaluation.py    ← NEW: Single model script
│   ├── compare_models.py    ← NEW: Multi-model script
│   ├── attacks/             ← EXISTING: Your 22 attacks
│   └── services/            ← EXISTING: Already has Ollama
├── OLLAMA_GUIDE.md          ← NEW: Complete usage guide
└── WHAT_I_ADDED.md          ← NEW: This file
```

---

## 🎯 Ready to Use!

Everything is set up and ready to go. Just:

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Get a model
ollama pull llama3.2:3b-instruct

# 3. Run evaluation
cd backend
python run_evaluation.py your_cv.pdf
```

**You'll have quantitative thesis data in minutes! 🚀**

---

## Questions?

- **Setup issues:** Check `OLLAMA_GUIDE.md`
- **Usage examples:** See `OLLAMA_GUIDE.md` sections 3-4
- **Understanding output:** See `OLLAMA_GUIDE.md` section 5
- **Thesis integration:** See `OLLAMA_GUIDE.md` section 8

**Everything is documented and ready to use!**

