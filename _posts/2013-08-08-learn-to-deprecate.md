---
title: "Learn to Deprecate"
layout: post
---

Learn to deprecate code. This does two things:

1. Gives the freedom of change
2. Provides intent and instruction for your users

Working on the [same piece of software for years](https://github.com/cbmi/avocado) can be an absolute joy, until the day comes when people actually start using it. When this occurs something happens. All the changes you make may break their code that is using your software.

For programmers in industry, this is obvious. If you break something, it costs your employer money (and potentially your job). For those in the open source space however, there are no true repercussions to drag around unwanted code.

Unless you _want_ people to use your code. Choosing to open source your software comes with an implicit responsibility to inform users of what has changed across versions.

_As an aside, don't confuse not being a good citizen of informing users with the release of liability stated in a license such as MIT. If you want nothing to do with your users.. don't open source your code._

### Naysayers

Some users will ask why something _needs_ to change. Most things don't _need_ to change, but the assumption is that the change was made to improve the foundation for the API to evolve. The disconnect between the API developers and the users comes in two flavors:

- The micro (user) vs. macro (developer) perspective
- The user not wanting to do work to get new features

### The Process

The code portion is pretty straightforward:

- Ensure tests exist that use the current API
- Implement the new API and tests
- Ensure previous tests don't fail
- Document new APIs and deprecation notice
- Send out a notice to users via some medium

To alleviate the second point presented by the naysayers, deprecated APIs should be grouped together and **not** intermixed with new features. This reduces the cognitive load of the user when using the new version of your library. They can remove the deprecated APIs from their code in preparation for the next release (which most likely contain features that rely on the updated APIs).
