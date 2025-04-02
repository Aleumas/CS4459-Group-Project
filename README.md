# RAFT-Based Primary-Backup System

This system implements a simple fault-tolerant key-value store using the RAFT consensus algorithm. It supports leader election and log replication.

---

## How It Works

1. **Startup**
   - Each node loads its saved state and starts as a follower.
   - A monitor thread waits for heartbeats from a leader.

2. **Election**
   - If no heartbeat is received within a timeout, a node starts an election.
   - The node becomes a candidate and requests votes from peers.
   - If it gets a majority, it becomes the new leader.

3. **Leader Behavior**
   - Sends periodic heartbeats to followers.
   - Notifies the discovery server that it is the current leader.
   - Handles write requests from clients and replicates logs.

4. **Client Requests**
   - The client asks the discovery server for the current leader.
   - It sends a write request to the leader.
   - The leader replicates the request and commits it if acknowledged by a majority.

5. **Recovery**
   - Nodes save their state to disk and restore it on restart.
   - Restarted nodes rejoin as followers and participate in elections.

---

## How to Run the System

### If you're on Unix/Linux, then to run the system with 4 nodes just double click the .sh file:
```
.sh
```

### If you're on Windows, then to run with 4 nodes just double click the .bat file:
```
.bat
```

Each node stores its state in `node_state_<node_id>.json`. The client logs to `client.txt`.

For a minimal 4-node RAFT cluster, this setup provides leader election, log replication, and simple fault tolerance.
