---
layout: post
title: "Goroutines, Channels, and Select"
summary: "Example use of goroutines, channels and the select statement in Go."
published: true
---

This is a quick explanation of goroutines with timeouts using the `select` statement in Go.

Say you want to scrape the bodies of a few webpages. We can write a program that iterates over each url passed to the program, perform a `GET` request, and write the body to a temporary file.

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
    defer resp.Body.Close()
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
	temp, _ := ioutil.TempFile(".", fmt.Sprintf("%v-", time.Now()))
    defer temp.Close()
    
    for _, url := range urls {
		body, _ := fetchBody(url)
        temp.Write(body)
    }
}
```

The problem with this approach is two-fold. Since we are working with _remote_ services, the work is naturally distributable (good) and we can't rely on the service to respond (bad). To handle the first problem we can wrap each call in a goroutine. Here is the modified for loop:

```go
for _, url := range urls {
    go func() {
        body, _ := fetchBody(url)
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
    	body, _ := fetchBody(url)
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
		body, _ := fetchBody(url)
    	temp.Write(body)
        done<- true
    }()
        
    select {
    case <-done:
    case <-time.After(time.Second):
    }
	counter<- true
}()
```

A goroutine inside _another_ goroutine!! Yes. The outer one initializes a `bool` channel for the inner goroutine to send on when it's done. The `select` statement will receive from `done` or timeout after one second. Note that the `counter` channel receives a value regardless since the goroutine has completed. This ensures the main goroutine does not block for timed out fetches.

The program should run in about one second since the operations are running in parallel and each operation times out after a second.

---

### Refactor

Based on [feeback](https://plus.google.com/106530954599911462020/posts/hKK1kxd6tE1) on Google+, here is a more robust implementation of `fetchBody` which handles canceling the request after a timeout has been reached.

To be able to cancel the request, the request itself needs to be referenced. Also, a plain HTTP client and transport are created to utilized the `Transport.CancelRequest` method if the timeout is reached. Here is the updated portion of code.

In addition, although I was looking for a idiomatic way to wait for a series of goroutines to finish using channels, I've replaced the polling loop with a `sync.WaitGroup`.

Here is the full updated code (thanks to [Bryan Mills](https://plus.google.com/102284724133933401859) for his review and help):

```go
package main

import (
    "fmt"
    "io/ioutil"
    "net/http"
    "os"
    "sync"
    "time"
)

// Custom client with transport for better control
var transport = http.Transport{}
var client = http.Client{
    Transport: &transport,
}

func fetchBody(url string, timeout time.Duration) ([]byte, error) {
    // Initialize request, send it in a goroutine so it can be closed
    // if the response exceeds the timeout.
    req, _ := http.NewRequest("GET", url, nil)

    // Set up the timer for canceling the request. Stop it if the
    // request succeeds
    timer := time.AfterFunc(timeout, func() {
        transport.CancelRequest(req)
        fmt.Println(url, "timed out")
    })
    defer timer.Stop()

    // This will block until it succeeds or is canceled
    resp, err := client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    return ioutil.ReadAll(resp.Body)
}

func main() {
    urls := os.Args[1:]

    if len(urls) == 0 {
        fmt.Println("nothing to do")
        return
    }

    // write all the bodies to a temporary file in the current directory
    // prefixed with the time
    temp, _ := ioutil.TempFile(".", fmt.Sprintf("%v-", time.Now()))
    defer temp.Close()

    // Wait group and timeout
    wg := sync.WaitGroup{}
    timeout := 500 * time.Millisecond

    for _, url := range urls {
        // Increment wait group for each URL
        wg.Add(1)

        go func(url string) {

            defer wg.Done()
            body, err := fetchBody(url, timeout)
            if err != nil {
                fmt.Println(err)
            } else {
                temp.Write(body)
            }
        }(url)
    }

    // Block until everyone is done
    wg.Wait()
}
```
