import grpc
from concurrent import futures
import time
import discovery_pb2
import discovery_pb2_grpc

class LeaderDiscoveryService(discovery_pb2_grpc.LeaderDiscoveryServicer):
    def __init__(self):
        self.leader_id = "node1"
        self.host = "localhost"
        self.port = 50051

    def WhoIsLeader(self, request, context):
        print(f"Current Leader: {self.leader_id} at {self.host}:{self.port}")
        return discovery_pb2.LeaderInfo(
            leader_id=self.leader_id,
            host=self.host,
            port=self.port
        )

    def UpdateLeader(self, request, context):
        self.leader_id = request.leader_id
        self.host = request.host
        self.port = request.port
        print(f"Leader updated: {self.leader_id} at {self.host}:{self.port}")
        return discovery_pb2.Empty()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    service = LeaderDiscoveryService()
    discovery_pb2_grpc.add_LeaderDiscoveryServicer_to_server(service, server)
    server.add_insecure_port("[::]:5050")
    print("Leader Discovery Server running on port 5050")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("Shutting down Discovery Server")
        server.stop(0)


if __name__ == "__main__":
    serve()
