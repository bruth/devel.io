---
layout: post
title: "Go Tip: Stdout MultiWriter"
---

Need to makes multiple copies of a command's stdout? Use [io.MultiWriter](http://golang.org/pkg/io/#MultiWriter).

```go
package main

import (
    "bytes"
    "fmt"
    "io"
    "os/exec"
)

func main() {
    // A few boring buffers...
    var b1, b2 bytes.Buffer

    // Echo something profound
    cmd := exec.Command("echo", "-n", "foo")

    // Remember a MultiWriter takes an number of arguments implementing
    // the io.Writer interface.
    cmd.Stdout = io.MultiWriter(&b1, &b2)

    // Run it!
    cmd.Run()

    // See the magic
    fmt.Println("b1:", b1.String())
    fmt.Println("b2:", b2.String())
}
```
