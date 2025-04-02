#!/bin/bash

gnome-terminal -- bash -c "source venv/bin/activate && python discovery.py; exec bash"

gnome-terminal -- bash -c "source venv/bin/activate && python raft.py node1 50051 node2,node3,node4; exec bash"
gnome-terminal -- bash -c "source venv/bin/activate && python raft.py node2 50052 node1,node3,node4; exec bash"
gnome-terminal -- bash -c "source venv/bin/activate && python raft.py node3 50053 node1,node2,node4; exec bash"
gnome-terminal -- bash -c "source venv/bin/activate && python raft.py node4 50054 node1,node2,node3; exec bash"

gnome-terminal -- bash -c "source venv/bin/activate && python client.py; exec bash"
