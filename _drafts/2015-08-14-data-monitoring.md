---
published: false
---

[Monitoring](https://en.wikipedia.org/wiki/Monitoring) can generalized as the process of observing something over time (the generations of today are experts at this since the advent of the smart phone). Understanding what monitoring *is* is not difficult, understanding *why* something is being monitored is more interesting. In general, something worth monitoring is *important* because how it changes (or not) over time can provide insights that are not available in a static context.

Monitoring is really just comparing a derivative of the state (dimension) of something now with what it was before.

In the software industry, the vast majority of monitoring applies to [server logs](https://en.wikipedia.org/wiki/Server_log) or [application performance](https://en.wikipedia.org/wiki/Application_performance_management). In both cases, dimensions are typically defined ahead of time and computed as the log or performance data is ingested. For completeness, the output is typically written to a [time series database](https://en.wikipedia.org/wiki/Time_series_database). If the dimension is a number, such as a count or average, the values can be displayed in a chart over time.

But what if the dimension is not a number?