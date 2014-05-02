---
layout: post
title: "Go Fan-Out Function"
published: false
---

Here is a [live example](http://play.golang.org/p/5-Vu8kK3yM) of the code below.

```go
import (
	"log"
	"math/rand"
	"sync"
	"time"
)

// fanIn takes zero or more channels and merges the received data to a
// single output channel. For efficiency, the output channel should be
// buffered to the number of inputs to prevent goroutines blocking each
// other.
func fanIn(inputs []chan []byte, output chan []byte, exit chan bool, timeout time.Duration) {
	if len(inputs) == 0 {
		log.Println("zero inputs")
		return
	}

	defer log.Println("cleaning up fanIn")

	// Used for the buffered channel size, wait group size, and
	// knowing how many signals to send out.
	size := len(inputs)

	// Local proxy for exit channel
	signal := make(chan bool, size)

	// Wait group for spawned routines used after exit is signaled
	wg := sync.WaitGroup{}
	wg.Add(size)

	// Spawn goroutines for each input channel
	for i, input := range inputs {
		log.Println("spawning input", i)

		go func(input chan []byte, i int) {
			defer log.Println("closing input", i)
			defer wg.Done()

			// for-select idiom, receive input and write to output until
			// exit signal is received
			for {
				select {
				case m := <-input:
					log.Printf("input %d -> %d\n", i, m)
					output <- m
				case <-signal:
					return
				}
			}
		}(input, i)
	}

	// Block until an exit signal has been received.
	<-exit

	// Start a "cleanup" timer to prevent routines from blocking indefinitely
	// when waiting for them to be done. If the timeout is reached, force the
	// exit.
	if timeout > 0 {
		timer := time.AfterFunc(timeout, func() {
			log.Println("timeout occurred")
			exit <- true
			return
		})
		log.Println("timer for", timeout, "started")
		defer timer.Stop()
	}

	// Signals all routines to finish (some or all may already be done)
	for i := 0; i < size; i++ {
		signal <- true
	}

	// Wait until all routines are done and exit
	wg.Wait()
	exit <- true
}
```

The log statements have been left in for visualizing what is happening and in what order. Here is a simple program to test the behavior:

```go
func main() {
    // 5 inputs, no timeout
    testFanIn(5, 0)
}

// Takes int denoting how many inputs are used by the fanIn function
// and a timeout. Use a timeout of 0 to never timeout.
func testFanIn(n int, timeout time.Duration) {
	// Array of `n` inputs channels
	inputs := make([]chan []byte, n)

	// Output channel
	output := make(chan []byte)

	// Exit channel
	exit := make(chan bool)

	// Seeded random number generator for populating the input channels
	r := rand.New(rand.NewSource(time.Now().UnixNano()))

	// Initialize and populate buffered input channels with a few messages
	for i := 0; i < n; i++ {
		inputs[i] = make(chan []byte, n)

		for j := 0; j < n; j++ {
			inputs[i] <- []byte{byte(r.Intn(20))}
		}
	}

	// Spawn fanIn in a goroutine
	go fanIn(inputs, output, exit, timeout)

	// Spawn goroutine to read and log the values from the output channel
	// as they are received.
	go func() {
		for m := range output {
			log.Println("output <-", m)
		}
	}()

	// Request exit
	log.Println("exit signaled")
	exit <- true

	// Wait for response from fanIn
	<-exit
	log.Println("exit confirmed")
}
```
