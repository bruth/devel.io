---
published: true
layout: post
title: "Go: Handling Arbitrary JSON"
date: {}
summary: "Go provides an interesting approach to decoding and encoding JSON to and from types. However, the type-safety could get in the way when handling JSON with an unknown structure. This post gives a quick introduction to the problem and one way of handling arbitrary JSON."
---

[Go](http://golang.org) provides the [encoding/json](http://golang.org/pkg/encoding/json/) package in it's standard library. The first thing I immediately wondered (and got hung up on) was how a statically typed language would handle decoding arbitrary JSON. Furthermore, Go [does not have a type hierarchy](http://golang.org/doc/faq#inheritance) nor support for [generics](http://golang.org/doc/faq#generics).

Let's begin.

Go has [interface types](http://golang.org/ref/spec#Interface_types):

> An interface type specifies a method set called its interface. A variable of interface type can store a value of any type with a method set that is any superset of the interface. Such a type is said to implement the interface. The value of an uninitialized variable of interface type is nil.

In practice this means functions and methods can be defined to expect and return types that implement an interface. Here is a simple and silly example:

```go
func Echo(i interface{}) (interface{}) {
	return i
}
```
_[Live example](http://play.golang.org/p/-nzvZnQpLc)_

The `Echo` function takes any type that implements the _empty_ interface. From the spec:

> A type implements any interface comprising any subset of its methods and may therefore implement several distinct interfaces. For instance, all types implement the empty interface.

From the [laws of reflection (in Go)](http://golang.org/doc/articles/laws_of_reflection.html):

> It represents the empty set of methods and is satisfied by any value at all, since any value has zero or more methods.

How does this help us?

The JSON package defines two functions `Marshal` and `Unmarshal` which handle the encoding and decoding of JSON, respectively. The `Unmarshal` function decodes JSON into two primary structures: `map[string]interface{}` and `[]interface{}` representing a JavaScript object and array, respectively. Since all types satisfy `interface{}`, each respective JSON type can be converted and contained within these structures.

```go
// Define an empty interface
var i interface{}
// Convert JSON string into bytes
b := []byte(`{"user_id": 1, "message": "Hello world"}`)
// Decode bytes b into interface i
json.Unmarshal(b, &i)
fmt.Println(i)
```

_[Live example](http://play.golang.org/p/QLRx22PJMF)_

Here is the cool part. `Unmarshal` can decode values into types that have fields with the same name as the JSON object keys.

```go
type Tweet struct {
    user_id int
    message string
}

var t Tweet
json.Unmarshal(b, &t)
fmt.Println(t)
```

_[Live example](http://play.golang.org/p/l0gh-SoQ2a)_

Un oh. If you are following along with the examples, the output would say `{0 }` (i.e. 0 and the empty string). Why didn't it set the two fields? Fields that start with a lowercase field name are [not exported](http://golang.org/ref/spec#Exported_identifiers) and thus are not accessible by external methods.

We can get around this by _tagging_ the type fields with metadata as [described] in the `Marshal` documentation.

```go
type Tweet struct {
    UserId int `json:"user_id"`
    Message string `json:"message"`
}

var t Tweet
json.Unmarshal(b, &t)
fmt.Println(t)
```

_[Live example](http://play.golang.org/p/P-BM9QdYjG)_

Ah, there we go. If you want to learn how this works under-the-hood, read up on the [reflect package](http://golang.org/pkg/reflect/#StructTag).

So. This is good, but there is still a problem. When JSON data contains fields _not_ defined in the types they are being decoded into, these fields are ignored. On one hand, this is definitely a feature when you _do_ want to ignore unknown fields, however if you do want to include them, we need to override how a `Tweet` value is encoded.

How do we do this? First, a quick aside.

I've recently been working with the [labix.org/v2/mgo/bson](http://godoc.org/labix.org/v2/mgo/bson) package which provides a BSON API that mimics the Go's encoding/json API. As noted above, decoding JSON into a struct will ignore unknown fields, however the `bson.Unmarshal` fuction _does_ support unknown fields. It is supported through the use of an extra tag _flag_ called [inline](http://godoc.org/labix.org/v2/mgo/bson#Marshal). A field can be defined tagged with the "inline" flag and all data that doesn't unmarshal into the type's fields will be stored there.

So how to we solve our JSON issue? By using BSON in an intermediate during the encoding/decoding step. Yes, this requires a whole other package to provide this feature and is a bit of hack, but it solved my problem since I am using [mgo](http://labix.org/mgo) in my project.

The trick is to encode the tweet using the `bson.Marshal` function into a byte array, decoding it back into an empty interface value, then encoding and returning that value. Likewise, the `UnmarshalJSON` will decode the byte array into a map, re-encoded using `bson.Marshal` and finally decoded into the `Tweet` value.

```go
func (t *Tweet) MarshalJSON() ([]byte, error) {
    var j interface{}
    b, _ := bson.Marshal(t)
    bson.Unmarshal(b, &j)
    return json.Marshal(&j)
}

func (t *Tweet) UnmarshalJSON(b []byte) error {
    var j map[string]interface{}
    json.Unmarshal(b, &j)
    b, _ = bson.Marshal(&j)
    return bson.Unmarshal(b, t)
}
```

Given that we have this now, we can tack on an additional field onto `Tweet` dedicated to storing the extra stuff. We also need to add the `bson:"..."` tags so they are consistent with the JSON tag.

```go
type Tweet struct {
    UserId int `json:"user_id" bson:"user_id"`
    Message string `json:"message" bson:"message"`
    Extra map[string]interface{} `json:"-" bson:",inline"`
}
```

When all said and done, we can do this:

```go
b := []byte(`{
	"user_id": 1,
    "message": "Hello World",
    "location": {
    	"longitude": -47.38283,
        "latitude": 32.83282
    }
}`)
t := Tweet{}
json.Unmarshal(b, &t)
fmt.Println(t.Extra) // map[location:map[longitude:-47.38283 latitude:32.83282]]
```

The extra data will stored in the `Extra` field. We can confirm encoding works:

```go
b2, _ := json.Marshal(&t)
fmt.Println(string(b2))
```
This will merge the data in the `Extra` map back into the object.

### References

- [Golang JSON Package Docs](http://golang.org/pkg/encoding/json/)
- [JSON and Go](http://golang.org/doc/articles/json_and_go.html)
- [Go by Example: JSON](https://gobyexample.com/json)
- [mgo](http://labix.org/mgo)
- [mgo/bson docs](http://godoc.org/labix.org/v2/mgo/bson)