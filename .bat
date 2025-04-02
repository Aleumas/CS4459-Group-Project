start cmd /k "call venv\Scripts\activate && python discovery.py"

start cmd /k "call venv\Scripts\activate && python raft.py node1 50051 node2,node3,node4"
start cmd /k "call venv\Scripts\activate && python raft.py node2 50052 node1,node3,node4"
start cmd /k "call venv\Scripts\activate && python raft.py node3 50053 node1,node2,node4"
start cmd /k "call venv\Scripts\activate && python raft.py node4 50054 node1,node2,node3"

start cmd /k "call venv\Scripts\activate && python client.py"
