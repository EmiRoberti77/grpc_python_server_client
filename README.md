# gRPC Python Example — Server & Client

This repository demonstrates how to build a **gRPC server and client in Python** using `grpcio` and `grpcio-tools`. It walks through:

- Writing a `.proto` service definition
- Generating Python code (`proto_pb2.py`, `proto_pb2_grpc.py`)
- Implementing the **server**
- Implementing the **client**
- Running and testing the system end-to-end

---

## 1. Install dependencies

It is recommended to use a Conda environment:

```bash
conda create -n pygrpc python=3.11 -y
conda activate pygrpc
pip install grpcio grpcio-tools protobuf
```

---

## 2. Project structure

```
src/
  app/
    server.py
    client.py
    proto/
      proto.proto
    generated/
      proto_pb2.py
      proto_pb2_grpc.py
```

- `proto.proto` → the gRPC service definition
- `server.py` → implements the service
- `client.py` → calls the service
- `generated/` → contains Python code generated from the `.proto`

---

## 3. Define the `.proto`

`src/app/proto/proto.proto`:

```proto
syntax = "proto3";

package emi_service;

service EmiService {
  rpc Start (StartRequest) returns (StartResponse) {}
}

message StartRequest {
  string command = 1;
}

message StartResponse {
  int32 status = 1;
  string message = 2;
}
```

---

## 4. Generate Python code

Run:

```bash
python3 -m grpc_tools.protoc   -I src/app/proto   --python_out=src/app/generated   --grpc_python_out=src/app/generated   ./src/app/proto/proto.proto
```

This produces:

```
src/app/generated/proto_pb2.py
src/app/generated/proto_pb2_grpc.py
```

---

## 5. Implement the server

`src/app/server.py`:

```python
import os, sys, grpc
from concurrent import futures

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)

from app.generated import proto_pb2 as pb2, proto_pb2_grpc as pb2_grpc

class EmiService(pb2_grpc.EmiServiceServicer):
    def Start(self, request, context):
        print(f"Received command: {request.command}")
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

## 6. Implement the client

`src/app/client.py`:

```python
import os, sys, grpc, argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)

from app.generated import proto_pb2, proto_pb2_grpc

def main(host="localhost", port=50051, command="RUN"):
    target = f"{host}:{port}"
    with grpc.insecure_channel(target) as channel:
        stub = proto_pb2_grpc.EmiServiceStub(channel)
        req = proto_pb2.StartRequest(command=command)
        resp = stub.Start(req)
        print(f"status={resp.status} message={resp.message}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=50051)
    parser.add_argument("--command", default="RUN")
    args = parser.parse_args()
    main(args.host, args.port, args.command)
```

---

## 7. Run the system

From project root:

### Start server
```bash
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
python3 src/app/server.py
```

Output:
```
gRPC server listening on 50051
```

### Run client (new terminal)
```bash
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
python3 src/app/client.py --command "hello world"
```

Output:
```
status=0 message=Started: hello world
```

---

## 8. How it works

1. **Define messages and services** in `.proto` (`StartRequest`, `StartResponse`, `EmiService`).
2. **Generate Python bindings** with `grpc_tools.protoc` → creates:
   - `proto_pb2.py` → message classes
   - `proto_pb2_grpc.py` → service stubs and base classes
3. **Server**:
   - Subclasses `EmiServiceServicer` and implements `Start`.
   - Registers itself with `add_EmiServiceServicer_to_server`.
   - Binds to port 50051 and listens for requests.
4. **Client**:
   - Creates a channel to `localhost:50051`.
   - Instantiates `EmiServiceStub`.
   - Calls `stub.Start(StartRequest(command=...))`.
5. **gRPC runtime**:
   - Handles serialization (to Protobuf) and network transport.
   - Delivers `StartResponse` back to the client.

---

## 9. Troubleshooting

- **No module named proto_pb2**  
  Ensure `src/app/generated` is in `PYTHONPATH` or imports are adjusted.
- **Connection refused**  
  Start server before client, confirm ports.
- **Permission denied**  
  Don’t bind to ports <1024 unless root/admin.

---

## Recap

- The `.proto` defines the contract (service + messages).
- `grpc_tools.protoc` generates Python code.
- `server.py` implements the service and runs the gRPC server.
- `client.py` connects to the server and calls methods.
- Together they demonstrate a working Python gRPC application.
