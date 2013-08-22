---
published: true
layout: post
title: "Go News: encoding/json inline flag for struct fields"
---

_Follow-up to [Go: Handling Arbitrary JSON]({% post_url 2013-08-19-go-handling-arbitrary-json %})._

Discussion on [golang-nuts](https://groups.google.com/forum/#!topic/golang-nuts/bAgNll-EMkI) led to me filing a [ticket](https://code.google.com/p/go/issues/detail?id=6213) for supporting the `inline` tag for struct fields in the `encoding/json` package. It has been accepted and targeted for the 1.2 release.