# Environment Setup — Conda & Dependencies

This document explains how to set up a Conda environment for the gRPC Python server/client project, including required dependencies.

---

## Why Conda?

Using Conda provides:

- Easy management of Python versions (e.g., 3.10, 3.11, 3.12).
- Precompiled binaries for heavy dependencies like `grpcio` and `protobuf`.
- Separation of project dependencies from system Python.

---

## Step 1: Create and activate environment

```bash
# Add conda-forge for best coverage
conda config --add channels conda-forge
conda config --set channel_priority strict

# Create a new environment
conda create -n pygrpc python=3.11 -y

# Activate it
conda activate pygrpc
```

---

## Step 2: Install dependencies

Core dependencies:

```bash
# Using conda
conda install grpcio grpcio-tools protobuf -y

# Alternatively, inside the env you can use pip
pip install grpcio grpcio-tools protobuf
```

Optional extras:

```bash
pip install grpcio-status mypy-protobuf ruff black
```

- `grpcio-status` → helpers for richer error handling.
- `mypy-protobuf` → generate typing info from protos.
- `ruff`, `black` → linting/formatting.

---

## Step 3: Verify installation

```bash
python -c "import grpc, grpc_tools, google.protobuf; print('gRPC + Protobuf OK')"
```

You should see:

```
gRPC + Protobuf OK
```

---

## Step 4: Environment file (share with team/CI)

Save dependencies in `environment.yml`:

```yaml
name: pygrpc
channels:
  - conda-forge
dependencies:
  - python=3.11
  - grpcio
  - grpcio-tools
  - protobuf
  - pip
  - pip:
      - grpcio-status
      - mypy-protobuf
```

Then others can set up with:

```bash
conda env create -f environment.yml
conda activate pygrpc
```

---

## Step 5: Deactivate or remove

- Stop the environment:

```bash
conda deactivate
```

- Remove it completely:

```bash
conda remove -n pygrpc --all -y
```

---

## Summary

1. Create env → `conda create -n pygrpc python=3.11`
2. Activate → `conda activate pygrpc`
3. Install → `conda install grpcio grpcio-tools protobuf`
4. Verify → `python -c "import grpc"`
5. Deactivate when done → `conda deactivate`

This ensures a clean, isolated Python environment for your gRPC server and client.
