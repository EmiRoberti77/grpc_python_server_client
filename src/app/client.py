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