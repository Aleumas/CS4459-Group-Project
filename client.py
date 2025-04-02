import grpc
import raft_pb2
import raft_pb2_grpc
import discovery_pb2
import discovery_pb2_grpc
import time

def get_leader():
    try:
        with grpc.insecure_channel("localhost:5050") as channel:
            stub = discovery_pb2_grpc.LeaderDiscoveryStub(channel)
            response = stub.WhoIsLeader(discovery_pb2.Empty())
            return response.host, response.port
    except Exception as e:
        print(f"Failed to discover leader: {e}")
        return None, None

def send_request(stub, key, value):
    try:
        request = raft_pb2.LogRequest(key=key, value=value)
        response = stub.SendLogRequestAsLeader(request)

        if response.ack == "true":
            log(key, value)
            print(f"Committed: {key} -> {value}")
        elif response.ack == "not_leader":
            print(f"Not the leader. Leader is: {response.leader_id}")
        else:
            print("Log rejected or not committed")
    except Exception as e:
        print(f"Error during request: {e}")


def log(key, value):
    with open("client.txt", "a") as file:
        file.write(f"{key} {value}\n")

def run():
    counter = 1

    while True:
        host, port = get_leader()
        if not host or not port:
            print("Retrying discovery in 5 seconds...")
            time.sleep(5)
            continue

        try:
            with grpc.insecure_channel(f"{host}:{port}") as channel:
                stub = raft_pb2_grpc.RaftServiceStub(channel)
                key = str(counter)
                value = f"val_{counter}"
                send_request(stub, key, value)
                counter += 1
                time.sleep(5)
        except Exception as e:
            print(f"Connection error: {e}. Retrying...")
            time.sleep(5)

run()
