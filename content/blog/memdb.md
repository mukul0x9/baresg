---
title: "I Thought Redis Was Just a HashMap"
description: "a custom hash table implementation in golang"
date: "2026-06-04"
slug: "memdb"
summary: Building an in-memory database in Go.
tags: "recreational-programming,db"
---

when using an in-memory db like redis or memcached i used to think — isn't this just a global hash table with set/get/del operations? why don't people just use their language's built-in map, host it in the cloud, and call it a day?
  
so i thought, let's actually explore the internals and attempt to build a bare-bones version from scratch. i chose golang because i was exploring golang and its concurrency model.

## naive approach
started with go's native map with basic set/get/del over tcp. added goroutines per connection for concurrent requests. then the obvious problem — multiple goroutines reading and writing the same map. added a single mutex. works, but now every operation locks the entire table. anyway, was exploring different hash table implementations and came across a byte array approach from internet and decided to implement it and see what problems come up building from scratch.


## hash table 101
the basic idea is, hash the key, get an integer, use it as an array index. same key always hashes to the same index so avg-case lookups are O(1). but two different keys can hash to the same index, so we use chaining to store multiple values at the same index. like you can create object/struct to store key/value pairs with next pointer to next struct/object in chain. so now same index can store multiple key/value pairs via chaining (linked list). for collision resolution,there are other techniques as well like open addressing etc. 

i went with a byte array approach instead. which will have two arrays:

```
bucket_array [index → offset]
data_array   [keyLen | valLen | nextOffset | key | value | ...]

```
```
bucket[42] -> offset 128
data_array: [5|5|256|hello|world]
```

in this structure, we hash the key, get the bucket index, bucket stores an offset of the data in the data array.  data array stores the actual key/value pairs with metadata. each entry stores the data with next offset to next entry in chain. 

## sharding
the whole hash table still shares a single lock , every operation locks the entire table. we can split the table into multiple arrays, each entry in the array will have its own bucket array and data array. this way, we can lock only the array index we are working on, not the entire table.

``` go
type shard struct {
    mu          sync.RWMutex
    bucketArray []int
    dataArray   []byte
}

type DB struct {
    shards [NumShards]shard
}

func (db *DB) getShard(hash uint32) *shard {
    return &db.shards[hash%NumShards]
}
```
each shard is pre-allocated with a fixed size at startup. when a shard fills up , a background worker (goroutine) handles growing via channel queue so the whole operation does not block.

## delete and compaction 
the structure is append only in data array. so delete wont remove specific entry from chain. so i mark deleted entries with a tombstone value like `valLen = 0`. on get tombstone entries are skipped.
tombstone entries gonna accumulate and waste the memory space. added one compaction function which rebuilds the shard by skipping tombstone entries and this compaction is triggered when memory usage crosses a threshold. but it also locks the shard so it's a trade off.

## conclusion
built this purely for learning — but exploring memory management, concurrency, and go internals all at once was quite fun.

## did it actually help?

benchmarked SET-only with 100 concurrent connections against a plain
`sync.RWMutex` native map, monitored with `GODEBUG=gctrace=1`.

throughput (3 runs): native map 96k–116k RPS, custom hash table 88k–90k RPS.
max STW pause: native map ~1.5ms, custom hash table ~6ms.
max concurrent mark: native map ~113ms, custom hash table ~7.8ms.

native map wins on throughput and STW pause.

concurrent mark duration 113ms(native map) vs 7.8ms.

## what's missing
- no persistent storage, data is lost on restart
- no eviction policy, memory usage grows without bound
- no crash recovery
- compaction pauses the shard while rebuilding
- no replication
- edges case handling

source code: [https://github.com/mukul0x9/memdb](https://github.com/mukul0x9/memdb)

references: 
- [https://github.com/allegro/bigcache](https://github.com/allegro/bigcache)
- [https://github.com/coocood/freecache](https://github.com/coocood/freecache)
- [https://www.youtube.com/watch?v=h30k7YixrMo](https://www.youtube.com/watch?v=h30k7YixrMo)
