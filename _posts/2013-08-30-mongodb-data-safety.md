---
layout: post
title: "Notes: How to Keep Your Data Safe in MongoDB"
summary: Personal notes from watching the talk with a few links to the documentation where applicable.
---

_Notes from watching [How to Keep Your Data Safe in MongoDB](http://www.mongodb.com/presentations/how-keep-your-data-safe-mongodb)_

- Client-server interaction
    - Client sends a write operation to server
    - Received by server's TCP stack
    - MongoDB process queues write
    - Write happens in memory
    - Depending on what 'Write Concern' asks for
        - Respond immediately
        - Wait for data to be journaled, then respond
- Possible issues
    - Network can go down
        - Client doesn't know
    - Write could fail for a logical reason
        - Unique key exception
    - Server could crash
        - Pre-journaled - write is done
        - Post-journaled - write is safe
    - **Bottom line**: using a single server is risky
- Replica sets
    - Replication is async
    - Full copy of data
    - N nodes
    - [Write concern](http://docs.mongodb.org/manual/core/write-concern/) (_w_) defines the number nodes data must be written to before verifying the write is _safe_
        - Arbitrary number e.g. 2 nodes
        - Simple majority i.e. N/2 + 1 (preferred)
    - [Nodes can be tagged](http://docs.mongodb.org/manual/tutorial/configure-replica-set-tag-sets/) with key/value pairs
        - region=us-east,color=blue
        - Used to force a write behavior
    - Nodes can have priority, i.e. which are primary
- Product should give you the choices for your semantics
    - Fundamental different operations in application, i.e. write concern
- Observe error messages, make sure they match your assumptions
- Use arbiter to break simple majoriy ties to prevent read-only mode
    - 2 centers x 2 nodes + 1 arbiter (no data required)
