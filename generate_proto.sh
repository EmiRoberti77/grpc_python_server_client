python3 -m grpc_tools.protoc \
  -I src/app/proto \
  --python_out=src/app/generated \
  --grpc_python_out=src/app/generated \
  ./src/app/proto/proto.proto
