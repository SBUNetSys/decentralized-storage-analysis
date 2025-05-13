#!/bin/bash
export FULLNODE_API_INFO=https://api.node.glif.io
boost deal-status --provider=$1 --deal-uuid=$2
