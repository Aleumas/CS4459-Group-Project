import json
import os
import threading
import time
import grpc
import random
from enum import Enum
import raft_pb2
import raft_pb2_grpc
import discovery_pb2
import discovery_pb2_grpc

class Role(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

class LogEntry:
    def __init__(self, msg, term):
        self.msg = msg
        self.term = term

class Node:
    def __init__(self, node_id, peer_ids):
        self.node_id = node_id
        self.peer_ids = peer_ids
        self.currentTerm = 0
        self.votedFor = None
        self.log = []
        self.commitLength = 0
        self.currentRole = Role.FOLLOWER
        self.currentLeader = None
        self.votesReceived = set()
        self.sentLength = {}
        self.ackedLength = {}
        self.state_file = f"node_state_{node_id}.json"
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(5, 10)
        self.recoveryFromCrash()
        self.start_heartbeat_monitor()

    def start_heartbeat_monitor(self):
        def monitor():
            while True:
                time.sleep(1)
                if self.currentRole == Role.FOLLOWER:
                    print(f"{self.node_id} has last heartbeat at {self.last_heartbeat}")
                    if time.time() - self.last_heartbeat > self.election_timeout:
                        print(f"{self.node_id} is starting an election (timeout)")
                        self.leaderFailedOrElectionTimeout()
        threading.Thread(target=monitor, daemon=True).start()

    def leaderFailedOrElectionTimeout(self):
        self.currentRole = Role.CANDIDATE
        self.currentTerm += 1
        self.votedFor = self.node_id
        self.votesReceived = {self.node_id}
        self.persist_state()
        self.sendVoteRequests()

    def receivingVoteRequest(self, term, candidate_id):
        if term > self.currentTerm:
            self.currentTerm = term
            self.votedFor = None
            self.persist_state()

        if (self.votedFor is None or self.votedFor == candidate_id) and term >= self.currentTerm:
            self.votedFor = candidate_id
            self.persist_state()
            return True
        return False

    def receivingVoteResponse(self, vote_granted):
        if vote_granted:
            self.votesReceived.add(vote_granted)
        if len(self.votesReceived) > (len(self.peer_ids) + 1) // 2:
            print(f"votesReceived: {self.votesReceived} len(self.peer_ids): {len(self.peer_ids)}")
            self.becomeLeader()

    def becomeLeader(self):
        self.currentRole = Role.LEADER
        self.currentLeader = self.node_id
        for peer in self.peer_ids:
            self.sentLength[peer] = len(self.log)
            self.ackedLength[peer] = 0
        self.notifyDiscoveryService()
        threading.Thread(target=self.leaderUpdate, daemon=True).start()

    def notifyDiscoveryService(self):
        try:
            with grpc.insecure_channel("localhost:5050") as channel:
                stub = discovery_pb2_grpc.LeaderDiscoveryStub(channel)
                request = discovery_pb2.LeaderInfo(
                    leader_id=self.node_id,
                    host="localhost",
                    port=50050 + int(self.node_id[-1])
                )
                stub.UpdateLeader(request)
                print(f"Notified discovery service: I am the leader ({self.node_id})")
        except Exception as e:
            print(f"Failed to notify discovery service: {e}")

    def sendVoteRequests(self):
        for peer in self.peer_ids:
            try:
                port = 50050 + int(peer[-1])
                with grpc.insecure_channel(f"localhost:{port}") as channel:
                    stub = raft_pb2_grpc.RaftServiceStub(channel)
                    request = raft_pb2.VoteRequest(key=str(self.currentTerm), value=self.node_id)
                    response = stub.SendVoteRequest(request)
                    if response.ack == "granted":
                        self.receivingVoteResponse(peer)
            except Exception as e:
                print(f"Failed to contact {peer}")
        if self.currentRole == Role.CANDIDATE:
            self.currentRole = Role.FOLLOWER

    def leaderUpdate(self):
        while self.currentRole == Role.LEADER:
            self.replicateLog()
            time.sleep(2)

    def replicateLog(self):
        entry = self.log[-1] if self.log else LogEntry("", self.currentTerm)
        for peer in self.peer_ids:
            try:
                port = 50050 + int(peer[-1])
                with grpc.insecure_channel(f"localhost:{port}") as channel:
                    stub = raft_pb2_grpc.RaftServiceStub(channel)
                    request = raft_pb2.LogRequest(key=entry.msg, value=str(entry.term))
                    response = stub.SendLogRequestAsLeader(request)
                    if response.ack == "true":
                        self.receivingLogResponseAsLeader(peer)
            except Exception:
                pass

    def receivingLogRequestAsFollower(self, key, value, term):
        if term >= self.currentTerm:
            self.currentLeader = None
            self.last_heartbeat = time.time()
            self.log.append(LogEntry(key, term))
            self.commitLogEntries()
            self.persist_state()
            return True
        return False

    def receivingLogResponseAsLeader(self, peer_id):
        self.ackedLength[peer_id] += 1
        self.commitLogEntries()

    def appendEntries(self, key, value):
        self.log.append(LogEntry(key, self.currentTerm))
        self.persist_state()

    def commitLogEntries(self):
        for index in range(self.commitLength, len(self.log)):
            ack_count = 1
            for peer in self.peer_ids:
                if self.ackedLength.get(peer, 0) > index:
                    ack_count += 1
            if ack_count > len(self.peer_ids) // 2:
                self.commitLength = index + 1
                print(f"Node {self.node_id}: Committed log entry {index} -> {self.log[index].msg}")
                self.persist_state()
            else:
                break

    def persist_state(self):
        with open(self.state_file, "w") as f:
            json.dump({
                "currentTerm": self.currentTerm,
                "votedFor": self.votedFor,
                "log": [{"msg": e.msg, "term": e.term} for e in self.log],
                "commitLength": self.commitLength
            }, f)


    def recoveryFromCrash(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = json.load(f)
                self.currentTerm = state.get("currentTerm", 0)
                self.votedFor = None
                self.log = [LogEntry(**e) for e in state.get("log", [])]
                self.commitLength = state.get("commitLength", 0)

        self.currentRole = Role.FOLLOWER
        self.currentLeader = None
        print(f"[{self.node_id}] Term: {self.currentTerm}, Role: {self.currentRole}, Leader: {self.currentLeader}, CommitLen: {self.commitLength}")

    def log_state(self):
        print(f"[{self.node_id}] Term: {self.currentTerm}, Role: {self.currentRole}, Leader: {self.currentLeader}, CommitLen: {self.commitLength}")
