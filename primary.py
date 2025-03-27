from concurrent import futures
import time
import threading

import grpc
import replication_pb2
import replication_pb2_grpc
import heartbeat_service_pb2
import heartbeat_service_pb2_grpc


class Sequence(replication_pb2_grpc.SequenceServicer):
    dictionary = dict()

    def Write(self, request, context):
        backup_server_port = 50052

        try:
            with grpc.insecure_channel(f"localhost:{backup_server_port}") as channel:
                stub = replication_pb2_grpc.SequenceStub(channel)

                stub.Write(
                    replication_pb2.WriteRequest(key=request.key, value=request.value)
                )

                self.dictionary[request.key] = request.value

                self.log(request)

                return replication_pb2.WriteResponse(ack="true")

        except Exception as e:
            print(f"Error communicating with backup server: {str(e)}")
            return replication_pb2.WriteResponse(ack="false")

    def log(self, request):
        with open("primary.txt", "a") as file:
            file.write(f"{request.key} {request.value}\n")


def send_heartbeat():
    heartbeat_server_port = 50053
    try:
        with grpc.insecure_channel(f"localhost:{heartbeat_server_port}") as channel:
            stub = heartbeat_service_pb2_grpc.ViewServiceStub(channel)

            while True:
                stub.Heartbeat(
                    heartbeat_service_pb2.HeartbeatRequest(service_identifier="primary")
                )
                time.sleep(5)

    except Exception as e:
        print(f"Error communicating with heartbeat server: {str(e)}")


def server():
    port = 50051

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))

    replication_pb2_grpc.add_SequenceServicer_to_server(Sequence(), server)

    server.add_insecure_port(f"[::]:{port}")

    print("Primary server starting...")

    server.start()

    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()

    server.wait_for_termination()


server()
