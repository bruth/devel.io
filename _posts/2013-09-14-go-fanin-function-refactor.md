---
layout: post
title: "Go Fan-In Function Refactor"
---

I [previously wrote]({% post_url 2013-09-11-go-fanin-function %}) an implementation for a fan-in that takes N inputs and funnels data into one output. There were a few things I knew could be improved with regards to code clarity, idiomatic practices, and robustness.

I was recommended to read Dave Cheney's [Curious Channels](http://dave.cheney.net/2013/04/30/curious-channels) article for taking advantage of two distinct states of a channel, the _nil_ and _closed_ state. This article goes over the changes made and the reasoning behind them.

### Closed channels never block

...and nil channels always block (like an unbuffered channel that hasn't received a value yet).

```go
// Channel must be opened (initialized) before being closed
c := make(chan struct{})
close(c)
// Returns immediately
<-c
```

What is returned by a closed channel? The [zero value](http://golang.org/ref/spec#The_zero_value) of the channel's type, in this case `{}`. As an aside, there seems to be convention in the community (or at least from those pushing the convention) to define channels with a type `struct{}` that are only intended to be closed, i.e. the channel will not send or receive data while open.

The effect this has when used in a `select` statement is like a switch. The below example will spawn a goroutine that will either return after one minute or when `signal` can be receieved from. `signal` is immediately closed and thus the goroutine returns.

```go
signal := make(chan struct{})

go func() {
    select {
    case <-time.After(1 * time.Minute):
    case <-signal:
    }
}

close(signal)
```

In the first fan-in implementation, I used a loop that send a bool to a buffered channel (capped at the number of inputs) when the exit signal was received. It went from this:

```go
// Number of inputs
size := len(inputs)

// Local proxy for exit channel buffered to the number of inputs
signal := make(chan bool, size)

...

// Signals all routines to finish (some or all may already be done)
for i := 0; i < size; i++ {
    signal <- true
}
```

to this:

```go
// Local proxy for exit channel
signal := make(chan struct{})

...

// Signals all routines to finish
close(signal)
```

This is _much_ more elegant and certainly much more performant when `size` is large.

### Drain a channel without `range`

The fan-in implementation must receive values from all input channels when they are available and send it to the output channel. One way to do this is to use the `range` clause to receive from the input channel until it is closed.

```go
for v := range input {
    output<- v
}
```

Multiple inputs could be handle by simply spawning each loop in a separate goroutine. However, `range` will continue to loop or block until the `input` channel has been closed.

An alternate approach is to use a `for-select` construct which enables defining additional options during each step during communication. The question that needs to be asked when chosing to use a `select` statement is, if `input` is not yet ready to be received from, is there anything else that can be done in the meantime or as an alternative? The below show the same `for`-loop over `input`, but in a slightly difference structure.

```go
// Channel's initial state which is also the loop condition
open := true

for open {
    select {
    case v, open := input:
        if !open { break }
        output<- v
    case ...
    case ...
    }
}
```

It is typically good practice, if not necessary, to add a case for allowing timeouts. This is absolutely neccessary in programs that communicate to remote systems, since they can be unpredictable.

Another useful `case` statement to add is a _kill switch_. This can be implemented a couple ways, but since the fan-in function has N inputs, the simplest and cheapest way is to initialize `signal` as an unbuffered channel and to simply close it. All channels that reference the `signal` channel will immediately be able to receive from `signal` (remember closed channels never block).

```go
// Channel's initial state which is also the loop condition
open := true

for open {
    select {
    case v, open := input:
        if !open { break }
        output<- v
    case <-time.After(1 * time.Second):
        open = false
    case <- signal
        open = false
    }
}
```

### Wait, timeout or kill

The fan-in function supports a timeout that turns on once the exit signal is received. This allows any remaining goroutines to finish and clean themselves up being responding on the `exit` channel. The previous implementation had a subtle race condition in it that may or may not have mattered in practice, but it was not _sound_ code. Here is the previous code with some irrelevant bits stripped away.

```go
// Start a "cleanup" timer to prevent routines from blocking indefinitely
// when waiting for them to be done. If the timeout is reached, force the
// exit.
if timeout > 0 {
    timer := time.AfterFunc(timeout, func() {
        exit <- true
    })
    defer timer.Stop()
}

...

// Wait until all routines are done and exit
wg.Wait()
exit <- true
```

The `time.AfterFunc` is asynchronous which enables the rest of the program to run. If the program returns before the timeout is reached, it correctly stops the timer (which prevents the function from being called), however if the timeout is reached, the `exit` channel would be sent on twice. This is a race condition because if the send occurred in the timeout function, the program may shutdown before the second send occurs on `exit`, so the bug wouldn't be visible.

The new solution is must cleaner and makes use of the `signal` channel by closing it once the timeout (if supplied) has been reached.

```go
// Ensure a response is always sent on return
defer func() { exit<- true }()

...

// The exit channel is expected to send a true value and wait
// until it receives a response, however if it is closed,
// immediately signal the goroutines.
if _, ok := <-exit; !ok {
    close(signal)
} else if timeout > 0 {
    <-time.After(timeout)
    close(signal)
}

// Wait until all goroutines finish
wg.Wait()
```

There is no race condition and both the timeout and kill use the same mechanism for signaling the goroutines (one is just delayed).

### _Go play_ with the code

The final code is below and here is an example: http://play.golang.org/p/v_7mFkeJZH

```go
package main

import (
    "log"
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

    // Always signal the exit
    defer func() {
        exit <- true
    }()

    // Used to signal goroutines to exit
    signal := make(chan struct{})

    // Wait group for spawned routines used after exit is signaled
    wg := sync.WaitGroup{}
    wg.Add(len(inputs))

    // Spawn goroutines for each input channel
    for i, input := range inputs {
        log.Println("spawning input", i)

        // Spawn go routine for each input
        go func(input chan []byte, i int) {
            defer log.Println("closing input", i)
            defer wg.Done()

            open := true
            // for-select idiom to constantly receive off the input
            // channel until it is closed on it has been signaled
            // to exit
            for open {
                select {
                case value, open := <-input:
                    // Input is closed, break
                    if !open {
                        log.Println("(closed) input", i)
                        break
                    }
                    output <- value
                    log.Printf("input %d -> %d\n", i, value)
                case <-signal:
                    log.Println("(signaled) input", i)
                    open = false
                default:
                    open = false
                }
            }
        }(input, i)
    }

    // The exit channel is expected to send a true value and wait
    // until it receives a response, however if it is closed,
    // immediately signal the goroutines.
    if _, ok := <-exit; !ok {
        log.Println("exit channel closed")
        close(signal)
    } else if timeout > 0 {
        log.Println("timeout of", timeout, "started")
        <-time.After(timeout)
        close(signal)
    }

    // Wait until all routines are done and exit
    log.Println("waiting for goroutines to finish")
    wg.Wait()
}
```
