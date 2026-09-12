# Scripts Guide

This folder contains small local helper scripts.

Current scripts:

- `seed_data.py`: prints development sample creator and campaign JSON.
- `train_model.py`: placeholder showing planned ML feature names.

## Rules For Scripts

- Keep scripts small and easy to read.
- Do not put production business logic only in scripts.
- Do not commit secrets.
- Do not make scripts depend on real external APIs unless clearly documented.

## Running Scripts

From the repository root:

```bash
python3 scripts/seed_data.py
python3 scripts/train_model.py
```

These scripts are safe development helpers. They do not modify the database yet.
