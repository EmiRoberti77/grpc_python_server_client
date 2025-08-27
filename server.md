# `server.md` — gRPC Python Server (Explained)

This document explains, line-by-line, what the provided Python **gRPC server** does, why it does it, and how to run it safely. It also points out a few best practices and shows how to run the server alongside the client.

---

## File under review

```python
import os
import sys
from concurrent import futures
import grpc

# add src to sys.path so 'generated' package is visible
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)

from generated import proto_pb2 as pb2
from generated import proto_pb2_grpc as pb2_grpc

class EmiService(pb2_grpc.EmiServiceServicer):
    def Start(self, request, context):
        return pb2.StartResponse(status=0, message=f"Started: {request.command}")

def serve(port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_EmiServiceServicer_to_server(EmiService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"gRPC server listening on {port}")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
```

---

## Purpose

- Define and run a gRPC **server** for the `EmiService`.
- Implement the `Start` RPC method, which receives a `StartRequest` and returns a `StartResponse`.
- Expose the service on a TCP port (default `50051`).

---

## Dependencies

- `grpcio` (runtime)
- `grpcio-tools` (for generating stubs)
- The generated Python files:
  - `proto_pb2.py` (message classes: `StartRequest`, `StartResponse`)
  - `proto_pb2_grpc.py` (service base classes and registration functions)

---

## Walkthrough

### 1) Imports
```python
import os, sys, grpc
from concurrent import futures
```
- `grpc` provides server building blocks.
- `futures.ThreadPoolExecutor` runs requests concurrently in a thread pool.

### 2) Import path handling
```python
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)
```
- Adds `src/` to `sys.path`, making `generated` importable as a top-level package.

### 3) Generated stubs import
```python
from generated import proto_pb2 as pb2
from generated import proto_pb2_grpc as pb2_grpc
```
- `proto_pb2` contains message classes.
- `proto_pb2_grpc` contains:
  - `EmiServiceServicer` (base class you subclass to implement RPCs)
  - `add_EmiServiceServicer_to_server` (registers implementation with server)

### 4) Implement the service
```python
class EmiService(pb2_grpc.EmiServiceServicer):
    def Start(self, request, context):
        return pb2.StartResponse(status=0, message=f"Started: {request.command}")
```
- Inherits from generated `EmiServiceServicer`.
- Implements the `Start` RPC:
  - `request` is a `StartRequest` with `.command`.
  - Returns a `StartResponse` (two fields: `status`, `message`).

### 5) Create and run server
```python
def serve(port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_EmiServiceServicer_to_server(EmiService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"gRPC server listening on {port}")
    server.wait_for_termination()
```
- `grpc.server(...)` creates the gRPC server, backed by a thread pool for concurrent requests.
- Registers the service implementation with the server.
- `add_insecure_port("[::]:50051")` binds to all interfaces (IPv4/IPv6).
- `server.start()` launches the server asynchronously.
- `server.wait_for_termination()` keeps the process alive.

---

## Best Practices

- **TLS:** For production, replace `add_insecure_port` with `add_secure_port(credentials=...)`.
- **Graceful shutdown:** Handle `KeyboardInterrupt` to stop server cleanly.
- **Configurable port:** Consider using `argparse` for a `--port` flag.

---

## Fixed, robust version (recommended)

```python
import os
import sys
import grpc
from concurrent import futures

# Ensure src/ is on path
SRC_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SRC_ROOT not in sys.path:
    sys.path.append(SRC_ROOT)

from generated import proto_pb2 as pb2
from generated import proto_pb2_grpc as pb2_grpc


class EmiService(pb2_grpc.EmiServiceServicer):
    def Start(self, request, context):
        print(f"Received command: {request.command}")
        return pb2.StartResponse(status=0, message=f"Started: {request.command}")


def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_EmiServiceServicer_to_server(EmiService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"gRPC server listening on port {port}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down gRPC server...")
        server.stop(grace=None)


if __name__ == "__main__":
    serve()
```

---

## How to run

From project root:

```bash
# Ensure generated stubs exist
./generate_proto.sh

# Run server
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
python3 src/app/server.py
```

Expected output:

```
gRPC server listening on port 50051
```

In another terminal, run the client:

```bash
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
python3 src/app/client.py --command "hello world"
# status=0 message=Started: hello world
```

---

## Recap

- The server defines and registers the `EmiService` implementation.
- It listens on port 50051 for incoming gRPC calls.
- The `Start` RPC echoes back a message confirming the command.
- For production, use TLS, graceful shutdown, and configurable ports.
