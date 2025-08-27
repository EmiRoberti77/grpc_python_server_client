# `client.md` — gRPC Python Client (Explained)

This document explains, line-by-line, what the provided Python **gRPC client** does, why it does it, and how to run it safely. It also points out a few correctness issues and shows a fixed version.

---

## File under review

```python
import os
import sys
import grpc
import argparse

ROOT = os.path.abspath(os.path.join(os.path.join(__file__), '..'))
print(f"ROOT:{ROOT}")
sys.path.append(ROOT)

from src.app.generated import proto_pb2, proto_pb2_grpc

def main(host:str='localhost', port:int=50051, command:str = 'RUN')->None:
    target = f"{host}:{port}"
    with grpc.insecure_channel(target=target) as channel:
        stud = proto_pb2_grpc.EmiServiceStub(channel=channel)
        req = proto_pb2.StartRequest(command=command)
        resp = stud.Start(req)
        print(resp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=50051)
    parser.add_argument('--command', default='RUN2')
    args = parser.parse_args()
    main(args.host, args.port, args.command)
```

---

## Purpose

- Connect to a running **gRPC server** at `host:port`.
- Create a client **stub** for the `EmiService`.
- Send a `StartRequest(command=...)`.
- Print the returned `StartResponse`.

---

## Dependencies

- `grpcio` (runtime)
- `grpcio-tools` (only for generating stubs)
- The generated Python files:
  - `proto_pb2.py` (messages)
  - `proto_pb2_grpc.py` (service stubs)

These are usually placed in a folder like `src/generated/`.

---

## Walkthrough

### 1) Imports
```python
import os, sys, grpc, argparse
```
- `grpc` gives you channels and stubs.
- `argparse` parses `--host`, `--port`, `--command` from CLI.

### 2) Import path handling
```python
ROOT = os.path.abspath(os.path.join(os.path.join(__file__), '..'))
print(f"ROOT:{ROOT}")
sys.path.append(ROOT)
```
- Intent: add a directory to `sys.path` so `from ... import proto_pb2` works.
- **Issue:** `os.path.join(__file__, '..')` treats `__file__` as a file, not a directory; use `os.path.dirname(__file__)` instead.
- Also, adding this `ROOT` doesn’t make `src` a package—you usually want to add the **`src` directory** (project code root), not the file’s own folder.

### 3) Generated stubs import
```python
from src.app.generated import proto_pb2, proto_pb2_grpc
```
- **Issue:** This assumes a package hierarchy `src.app.generated`. In most projects, generated code lives at `src/generated`, so you’d import `from generated import proto_pb2, proto_pb2_grpc` *after* putting `src` on `sys.path`.

### 4) Main client logic
```python
target = f"{host}:{port}"
with grpc.insecure_channel(target=target) as channel:
    stud = proto_pb2_grpc.EmiServiceStub(channel=channel)
    req = proto_pb2.StartRequest(command=command)
    resp = stud.Start(req)
    print(resp)
```
- Builds a connection string `host:port`.
- **Note:** The canonical call is `grpc.insecure_channel(target)`; the `target=` keyword is not part of the public signature in older versions (positional is safest).
- Creates the service **stub**. (Variable name typo: `stud` → `stub`.)
- Constructs the request message and invokes the RPC.

### 5) CLI wrapper
```python
parser.add_argument('--host', '--port', '--command', ...)
```
- Lets you run: `python client.py --host 127.0.0.1 --port 50051 --command RUN`.

---

## Fixed, robust version (recommended)

Place this file at `src/app/client.py`. Generated stubs in `src/generated/`.

```python
import os
import sys
import grpc
import argparse

# Treat project `src/` as import root so `generated` is importable
SRC_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SRC_ROOT not in sys.path:
    sys.path.append(SRC_ROOT)

from generated import proto_pb2, proto_pb2_grpc


def main(host: str = "localhost", port: int = 50051, command: str = "RUN") -> None:
    target = f"{host}:{port}"
    with grpc.insecure_channel(target) as channel:
        stub = proto_pb2_grpc.EmiServiceStub(channel)
        req = proto_pb2.StartRequest(command=command)
        resp = stub.Start(req)
        # Pretty print: fields defined in your .proto (status, message)
        print(f"status={resp.status} message={resp.message}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EmiService gRPC client")
    parser.add_argument("--host", default="localhost", help="gRPC server host")
    parser.add_argument("--port", type=int, default=50051, help="gRPC server port")
    parser.add_argument("--command", default="RUN", help="Command to send")
    args = parser.parse_args()
    main(args.host, args.port, args.command)
```

**Why this works:**
- We compute `SRC_ROOT` using `os.path.dirname(__file__)` and add that **directory** to `sys.path`, exposing `generated` as a top-level package.
- We import `from generated import ...`, which matches the typical layout produced by `grpc_tools.protoc` when you output to `src/generated`.
- We use the positional argument for `grpc.insecure_channel(...)`.
- We rename `stud` → `stub` and print structured fields.

---

## How to run

From your **project root** (one level above `src/`):

```bash
# Start the server
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
python3 src/app/server.py
```

In another terminal:

```bash
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
python3 src/app/client.py --command "hello world"
# status=0 message=Started: hello world
```

> If your generated file `proto_pb2_grpc.py` still contains `import proto_pb2` (flat import) and not `from . import proto_pb2`, also add `$(pwd)/src/generated` to `PYTHONPATH` or patch the import to be relative.

---

## Troubleshooting

- **`ModuleNotFoundError: generated`**  
  Ensure you added `src` to `PYTHONPATH` or appended `SRC_ROOT` to `sys.path` as shown.

- **`ModuleNotFoundError: proto_pb2` inside `proto_pb2_grpc.py`**  
  The generator uses a flat import. Either:
  - Add `src/generated` to `PYTHONPATH`, **or**
  - Edit the first import in `proto_pb2_grpc.py` to `from . import proto_pb2 as proto__pb2` and ensure `src/generated/__init__.py` exists.

- **`UNAVAILABLE` or connection refused**  
  Server isn’t running or port differs. Confirm `host`, `port`, and firewall.

- **TLS needed**  
  Replace `grpc.insecure_channel` with `grpc.secure_channel(target, credentials)` and supply appropriate `ssl_channel_credentials()`.

---

## Recap

- The client builds a channel to `host:port`, creates an `EmiServiceStub`, sends `StartRequest`, and prints `StartResponse`.
- Import-path hygiene is critical: treat `src/` as your import root and import `generated` from there.
- Use the fixed version above to avoid subtle path and API issues.
