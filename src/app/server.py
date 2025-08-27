import os
import grpc
from concurrent import futures
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"ROOT:{ROOT}")
sys.path.append(ROOT)
from src.app.generated import proto_pb2, proto_pb2_grpc

class EmiService(proto_pb2_grpc.EmiService):
    def Start(self, request, context):
        return proto_pb2.StartResponse(status=200, message=f"Starte:{request.command}")
    

def serve(port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    proto_pb2_grpc.add_EmiServiceServicer_to_server(EmiService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"gRPC server listening on port:{port}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()