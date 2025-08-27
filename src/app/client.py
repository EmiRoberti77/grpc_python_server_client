import os
import sys
import grpc
import argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"ROOT:{ROOT}")
sys.path.append(ROOT)

from app.generated import proto_pb2, proto_pb2_grpc

def main(host:str='localhost', port:int=50051, command:str = 'RUN', method:str = 'start')->None:
    target = f"{host}:{port}"
    with grpc.insecure_channel(target=target) as channel:
        stub = proto_pb2_grpc.EmiServiceStub(channel=channel)
        if method.lower() == 'start':
            req = proto_pb2.StartRequest(command=command)
            resp = stub.Start(req)
        elif method.lower() == 'stop':
            req = proto_pb2.StopRequest(command=command)
            resp = stub.Stop(req)
        else:
            print(f"Unknown method: {method}. Use 'start' or 'stop'")
            return
        print(resp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=50051)
    parser.add_argument('--command', default='RUN2')
    parser.add_argument('--method', default='start', choices=['start', 'stop'], help='RPC method to call')
    args = parser.parse_args()
    main(args.host, args.port, args.command, args.method)