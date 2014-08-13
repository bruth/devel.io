---
layout: post
title: "Musing #138: Service First Design"
summary: "The primary API of a system should be a service accessible on the Web."
---

An [application programming interface (API)](http://en.wikipedia.org/wiki/Application_programming_interface) is a means to an end. Consumers of APIs ultimately care about *what* actions they can perform and the output they can obtain to support their needs. Good API design ensures that the API's methods and output match the mental model of the consumers within the domain as well as accomodate the common usage patterns of the consumers.

*I will clarify that I am referring to the *primary* API of a system, not API design for client libraries to an existing interface.*

---

Until recently, my natural instinct when thinking about designing a new API was to start coding something in *my* favorite language. Hypocritically, when I read about a new project that solves one of my needs only to find out that it is written in a language I am not familiar with, I typcailly close the tab.

**Designing an API in a programming language immediately limits the audience that can or are willing to use it.**

However, it is rarely the language itself that is the concern. All languages follow certain idioms and have various constraints that influences an API's design. Most languages require a runtime to be installed in order to execute code written in the language. Runtimes may behave slightly differently across platforms. The language's community may even have a cultural impact on how the API is [developed over time](http://www.reddit.com/r/ruby/comments/175gh3/is_it_usual_for_rubies_and_gems_to_lose_backwards/).

Futhermore, your favorite language may not be anyone elses. Anyone who is not you or one of the core developers of the API are consumers. I've heard this response many times:

> Oh, you want to use language X for this project? The rest of the team doesn't know language X. Either use a language they all know or make sure you set aside time to teach the rest of the team the language.

The culmination of these observations led me to the following claim:

**The _primary_ API of a system should be a service accessible on the Web.**

Why? The Web is the most ubiquitious platform and will likely always be in some form or another. For context, the concepts that converged into this musing include (not necessarily in chronological order):

- Jeff Bezos [mandated for "service interfaces"](http://apievangelist.com/2012/01/12/the-secret-to-amazons-success-internal-apis/) at Amazon in 2002. AWS followed.
- Martin Folwer introduces the concept of [microservices](http://martinfowler.com/articles/microservices.html) to replace traditional monolithic [SOA](http://en.wikipedia.org/wiki/Service-oriented_architecture) approaches.
- Russ Miles extends the concept of microservices by designing for ["antifragility"](http://www.infoq.com/articles/russ-miles-antifragility-microservices)
- [Vagrant](http://www.vagrantup.com/) and now [Docker](https://www.docker.com/) has completely changed how we think about "environments" by abstracting it away from the consumer. This has led to simpler and less fragile deployments making continous integration and deployment not only possible, but the new "norm".
- Analogously, the [rapid rise of mobile devices](http://www.gartner.com/newsroom/id/2408515) has necessitated the [mobile first](http://designshack.net/articles/css/mobilefirst/) movement in client-side Web development.
- The increase of Internet-ready devices such as mobile devices and ["wearables"](http://en.wikipedia.org/wiki/Wearable_computer) constitute the [Internet of Things (IoT)](http://en.wikipedia.org/wiki/Internet_of_Things)
- Many startups build ["mashup" applications](http://en.wikipedia.org/wiki/Mashup_(web_application_hybrid)) that depend almost entirely on other Web services and general cloud services.
- [Webhooks](http://en.wikipedia.org/wiki/Webhook) are being used to create communication pipelines across services on the Web.

It is obvious that designing a service for the Web is advantageous due to the breadth and depth of potential consumers, but more importantly the Web uses a "language" (protocol) understood and spoken by all consumers. The "runtime" of the Web is built-in to these devices. The conventions and idioms are well understood and converging to architectural styles such as [REST](http://en.wikipedia.org/wiki/Representational_state_transfer).

VMs and containers now make it possible to develop a service in any programming language you, the developer, want with any set of libraries, system services, etc. without having to expose any of it to the consumers. Although Docker containers certainly can run multiple processes, it is encouraged to only expose *one* of those as a service to consumers, either users or other containers.

The culmination of this idea can be translated into two practical steps:

- Develop containers for each of the systems or processes used by the service. This takes the microservices approach which makes it possible to scale individual proceses by run more of those containers.
- Develop a "consumer" container that exposes the Web API for the service. This container talks to the systems in the other containers and should be completely stateless. This enables running multiple "consumer" containers in parallel to handle more traffic if the need arises.

Anyone who has built a Web service will likely say, "um, yea.. that is how you architect a scaleable service normally". The difference is that since containers abstract away the host system and are cheap to run, there is no longer a requirement to deploy the service into "the cloud", a laptop will work just fine.
