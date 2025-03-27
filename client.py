import grpc
import replication_pb2
import replication_pb2_grpc


def run():
    port = 50051
    try:
        with grpc.insecure_channel(f"localhost:{port}") as channel:
            stub = replication_pb2_grpc.SequenceStub(channel)
            request = replication_pb2.WriteRequest(key="1", value="book")

            log(request)
            response = stub.Write(request)

            print("ACK: " + response.ack)
    except Exception as e:
        print(f"Error communicating with primary server: {str(e)}")


def log(request):
    with open("client.txt", "a") as file:
        file.write(f"{request.key} {request.value}\n")


run()
