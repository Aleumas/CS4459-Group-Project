import threading
from concurrent import futures
from datetime import datetime

import grpc
import heartbeat_service_pb2
import heartbeat_service_pb2_grpc


class ViewService(heartbeat_service_pb2_grpc.ViewServiceServicer):
    last_received = dict()
    running_checks = dict()

    def Heartbeat(self, request, context):
        identifier = request.service_identifier

        if identifier in self.running_checks:
            self.running_checks[identifier].cancel()
            del self.running_checks[identifier]

        self.last_received[identifier] = datetime.now()
        self.log(identifier, True)

        timer = threading.Timer(5.2, self.fail_check_health, args=[identifier])
        timer.daemon = True

        timer.start()
        self.running_checks[identifier] = timer
        return heartbeat_service_pb2.HeartbeatResponse()

    def fail_check_health(self, identifier):
        self.log(identifier, False)

    def log(self, server_identifier, is_present):
        state = "is alive" if is_present else "might be down"
        with open("heartbeat.txt", "a") as file:
            file.write(
                f"{server_identifier.capitalize()} {state}. Latest heartbeat received at {self.last_received[server_identifier]}\n"
            )


def server():
    port = 50053
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    heartbeat_service_pb2_grpc.add_ViewServiceServicer_to_server(ViewService(), server)
    server.add_insecure_port(f"[::]:{port}")
    print("Heartbeat server starting...")
    server.start()
    server.wait_for_termination()


server()
