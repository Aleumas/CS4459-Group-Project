# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: raft.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'raft.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nraft.proto\")\n\x0bVoteRequest\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\"\x1b\n\x0cVoteResponse\x12\x0b\n\x03\x61\x63k\x18\x01 \x01(\t\"(\n\nLogRequest\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\"\x1a\n\x0bLogResponse\x12\x0b\n\x03\x61\x63k\x18\x01 \x01(\t2r\n\x0bRaftService\x12.\n\x0fSendVoteRequest\x12\x0c.VoteRequest\x1a\r.VoteResponse\x12\x33\n\x16SendLogRequestAsLeader\x12\x0b.LogRequest\x1a\x0c.LogResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_VOTEREQUEST']._serialized_start=14
  _globals['_VOTEREQUEST']._serialized_end=55
  _globals['_VOTERESPONSE']._serialized_start=57
  _globals['_VOTERESPONSE']._serialized_end=84
  _globals['_LOGREQUEST']._serialized_start=86
  _globals['_LOGREQUEST']._serialized_end=126
  _globals['_LOGRESPONSE']._serialized_start=128
  _globals['_LOGRESPONSE']._serialized_end=154
  _globals['_RAFTSERVICE']._serialized_start=156
  _globals['_RAFTSERVICE']._serialized_end=270
# @@protoc_insertion_point(module_scope)
