---
published: false
layout: post
title: "Goroutines, Channels, and Select"
summary: "Example use of goroutines, channels and the select statement in Go."
---

This is a quick explanation of goroutines with timeouts using the `select` statement in Go.

Say you want to scrape the bodies of a few webpages. We can write a program that iterates over the urls passed to the program and performs a `GET` to receive the response and we write the body to a temporary file.

```go
package main

import (
	"fmt"
    "os"
	"bytes"
    "net/http"
    "io/ioutil"
)

func fetchBody(url string) ([]byte, error) {
	resp, err := http.Get(url)
    if err != nil {
    	return "", err
    }
    var b bytes.Buffer
    _, err = b.ReadFrom(resp.Body)
    return b, err
}

func main() {
	urls := os.Args[1:]
    
    if len(urls) == 0 {
    	fmt.Println("nothing to do")
        return
    }
    
    // write all the bodies to a temporary file in the current directory
    // prefixed with the time
   	temp, _ := ioutil.Tempfile(".", fmt.Sprintf("%v-", time.Now()))
    defer temp.Close()
    
    for _, url := range urls {
		body, err := fetchBody(url)
        temp.Write(body)
    }
}
```

The problem with this approach is two-fold. Since we are working with _remote_ services, the work is naturally distributable (good) and we can't rely on the service to respond (bad). To handle the first problem we can wrap each call in a goroutine. Here is the modified for loop:

```go
for _, url := range urls {
    go func() {
        body, err := fetchBody(url)
        temp.Write(body)
    }()
}
```

Hmm.. well we introduced a new problem. The `main()` function ends before any of the goroutines finish. Let's fix that by adding a channel for the goroutines to communicate on. This is known as a _buffered_ channel which means the channel is capped, but more importantly writes are asynchronous so the channel does not block until the channel is full.

```go
// Buffered channel
counter := make(chan bool, len(urls))

for _, url := range urls {
	go func() {
    	body, err := fetchBody(url)
        temp.Write(body)
        counter<- true
    }()
}

// Poll until all go routines have finished
for {
	if len(counter) == cap(counter) {
    	break
    }
    // Sleep to prevent the tight loop from blocking
    time.Sleep(10 * time.Millisecond)
}
```

The `for` loop simply polls to wait until `counter` has filled up.

_As an aside, `counter` could just be an integer that gets incremented by each goroutine, but it is more idiomatic (and better for refactoring) to use channels between goroutines._

Now let's fix the reliability issue. Servers can be down or can take a long time to respond, so we don't want our program waiting too long to finish. We can _select_ between returning the response body or timing out, whichever comes first. The body of the for loop can be modified:

```go
go func() {
	done := make(chan bool, 1)
    
	go func() {
		body, err := fetchBody(url)
    	temp.Write(body)
        done<- true
    }
        
    select {
    case <-done:
    case <-time.After(time.Second):
    }
	counter<- true
}()
```

A goroutine inside _another_ goroutine!! Yes. The outer one initializes a `bool` channel for the inner goroutine to send on when it's done. The `select` statement will receive from `done` or timeout after one second. Note that the `counter` channel receives a value regardless since the goroutine has completed. This ensures the main goroutine does not block for timed out fetches.

The most the program should run is about one second since each operation cannot exceed one second and they are running in parallel.