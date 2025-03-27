import grpc
from concurrent import futures
import time
import raft_pb2
import raft_pb2_grpc
from raft_node import Node

class RaftService(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, node):
        self.node = node

    def SendVoteRequest(self, request, context):
        candidate_id = request.value
        term = int(request.key)
        vote_granted = self.node.receivingVoteRequest(term, candidate_id)
        return raft_pb2.VoteResponse(ack="granted" if vote_granted else "rejected")

    def SendLogRequestAsLeader(self, request, context):
        success = self.node.receivingLogRequestAsFollower(
            key=request.key, value=request.value, term=self.node.currentTerm
        )
        return raft_pb2.LogResponse(ack="true" if success else "false")


def serve(node_id, peer_ids, port):
    node = Node(node_id, peer_ids)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_pb2_grpc.add_RaftServiceServicer_to_server(RaftService(node), server)
    server.add_insecure_port(f"[::]:{port}")
    print(f"RAFT node {node_id} running on port {port}...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("Shutting down...")
        server.stop(0)


if __name__ == "__main__":
    import sys

    this_node = sys.argv[1]
    port = int(sys.argv[2])
    peer_nodes = sys.argv[3].split(",") if len(sys.argv) > 3 else []
    serve(this_node, peer_nodes, port)
