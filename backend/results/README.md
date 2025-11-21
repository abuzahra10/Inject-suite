# Results Directory Layout

```
backend/results/
├── matrix_runs/
│   ├── api/              # UI-triggered automation lab runs
│   ├── gpu/              # GPU-specific sweeps
│   ├── enhanced/         # Experimental enhanced guardrail sweeps
│   ├── evasion/          # Evasion-focused experiments
│   └── legacy/           # Legacy scripts/older format runs
└── single_runs/
    ├── full_cv/          # Full CV sweeps executed via CLI
    └── pi/               # Misc prompt-injection experiments
```

Each run folder keeps the same internal structure (`poisoned_pdfs/`, `evaluation/<model>/<defense>/`, `run_metadata.json`).
