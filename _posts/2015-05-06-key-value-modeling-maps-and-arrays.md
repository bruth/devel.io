---
layout: post
title: "Key-value Modeling: Maps and Arrays"
summary: "Two techniques for modeling maps and arrays in a key-value store."
---

Key-value stores are generally considered to be low-level in the realm of databases and storage engines. The attraction comes from the ability to control how data is organized, when it is written and when it is accessed. The tradeoff is that common data structures like arrays and maps are not natively supported, however they can be *represented*. Below are a few techniques for representing the two most common data structures, map and array, in a key-value store.

Before we start, there are two practical considerations to keep in mind. Most key-value stores use strings or byte arrays for keys and byte arrays for values. This poses two questions.

### What conventions should be followed for defining keys?

Since key-value stores does not provide a higher level of organization (e.g. tables), keys that correspond to a logical group need to be manually separated. This is done by prepending a prefix to the key which acts as a namespace. The granularity of this namespace will vary from application to application.

### How should the value be encoded?

Since key-value stores store bytes, one must decide the encoding strategy to use for the values. A few questions can arise:

**Does the encoded data need to be portable?**

If the key-value store is not the only consumer of the bytes, then an encoding should be selected that can be *decoded* by each consumer. For example, a non-portable format would be [Python's pickle](https://docs.python.org/3/library/pickle.html) encoding. A very portable format would be something like [JSON](http://json.org) since virtually all programming languages have libraries for decoding JSON.

**Do specific data types needs to be supported?**

Some formats have limited supported for data types specifically when it comes to precision. The common tradeoff is simplicity and portability for speed and/or space. For example, JSON just has a *number* represented in various ways, but does not annotate whether it is an `int32`, `int64`, `float32`, etc. On the opposite side, Google's Protocol Buffers *does* differentiate between these types for performance reasons. For weakly typed values, encoders and decoders needs to detect the required bits and choose an appropriate method for handling the values. Strongly typed encoders already have this information and can blindly handle the value.

It is worth pointing out that these details are usually transparent, but it is something to be aware of when choosing an encoder.

### Map

The most straightforward data structure to represent is a map (also know as a hash or dictionary). This is because the key-value store itself is one big map!

A simple example (using [Go](http://golang.org) for no other reason than expressing types):

```go
bob := map[string]string{
    "name": "Bob Smith",
    "email": "bob@gmail.com",
    "address": "123 Bob Avenue Philadelphia, PA 19107",
}
```

To *set* this map, we can loop the keys and perform the set operations.

```go
for attr, value := range bob {
    // Prefix the key with the "bob" namespace.
    key = fmt.Sprintf("bob.%s", attr)

    // Convert string values to bytes
    kv.Set(key, []byte(value))
}
```

That was easy, but how do you get the data back out? What if you don't know *all* the keys associated with bob?

One strategy for handling this is to encode the keys together in the top-level namespace (i.e. `bob`) and then loop through the array of keys to perform the `get`s. In addition to set the key above, we would build an array of keys and set that too.

```go
// SetMap takes denormalizes a map and stores it given a key.
func SetMap(k string, m map[string]string) error {
    // Allocate an array equal to the size of the map.
    attrs := make([]string, len(m))

    i := 0

    for attr, value := range m {
        attrs[i] = attr
        i++

        key = fmt.Sprintf("%s.%s", k, attr)
        kv.Set(key, []byte(value))
    }

    // Example of encoding the keys.
    value, err := json.Marshal(attrs)

    if err != nil {
        return err
    }

    kv.Set(k, value)

    return nil
}
```

Now we store `bob`.

```go
SetMap("bob", bob)
```

To decode this structure, the application only needs to know that `bob` exists.

```go
func GetMap(k string) (map[string]string, error) {
    // Get the bytes
    bytes := kv.Get("bob")

    // Decode the attribute names for bob.
    attrs, err := json.Unmarshal(bytes)

    if err != nil {
        return nil, err
    }

    // Allocate a map equal to the size of the attrs array.
    m := make(map[string]string, len(attrs))

    // Get the value for the attributes.
    for _, attr := range attrs {
        key = fmt.Sprintf("%s.%s", k, attr)

        // Convert bytes back to a string.
        m[attr] = string(kv.Get(key))
    }

    return m, nil
}
```

And

```go
bob, _ := GetMap("bob")
```

### Array

An array can be thought of as a map with integer keys.

```go
friends := []string{"joe", "suzy", "bill"}
```

Just like the map, we need to keep information about the structure itself, in this case the length of the array. This is much simpler than the map since we can store a single integer.

```go
func SetArray(k string, a []string) error {
    for i, value := range a {
        key := fmt.Sprintf("%s.%d", k, i)

        kv.Set(key, []byte(value))
    }

    // Convert int to bytes using a 4 byte buffer..
    value := make([]byte, 4)
    binary.PutVarint(value, len(a))

    kv.Set(k, value)
}
```

Set friends.

```go
SetArray("friends", friends)
```

Just like before, when we want to read the structure we decode the top-level key first and use it to lookup of the content.

```go
func GetArray(k string) ([]string, error) {
    value := kv.Get(k)

    // Convert bytes to integer.
    length := binary.Varint(value)

    // Allocate the friends array.
    a := make([]string, length)

    for i := 0; i < length; i++ {
        key := fmt.Sprintf("%s.%d", k, i)

        a[i] = string(kv.Get(key))
    }

    return a, nil
}
```

Get friends.

```go
friends, _ := GetArray("friends")
```

### Discussion

The motivation for this approach is for modeling data representing the [state](https://en.wikipedia.org/wiki/State_(computer_science)) of something. Keeping the individual content separate enables accessing and updating the values independently. The alternative is to encode and store the whole structure, however this requires getting and decoding the whole structure just to update one part of the state. Furthermore, if structure is being shared in any way, decoupling the structure enables parallel access which relieves contention. Of course, *what* is being shared is application-specific and *how* the shared data is accessed needs to be thoroughly evaluated.

Using this approach to naively store maps and array with arbitrary data, such as user-defined documents is generally a bad idea. This is what document databases are which are optimized for random reads and writes within a document. However if the document types are known and the access patterns are controlled, this approach *may* be appropriate in some cases.

### Atomicity and Consistency

An obvious problem with the basic implementation above is that there are no atomicity guarantees when writing data nor consistency guarantees when reading data. Any of the data could be changed in the store between a *set* or *get* operation. If this is a problem, then a key-value store with transactions or atomic multi-set or get operations can be used. Another approach is to encode and store the *synchronized* content together so the write is atomic and reads are consistent.

### Resources

An influence for this post is a very thorough overview of [NoSQL Data Modeling Techniques](https://highlyscalable.wordpress.com/2012/03/01/nosql-data-modeling-techniques/).
