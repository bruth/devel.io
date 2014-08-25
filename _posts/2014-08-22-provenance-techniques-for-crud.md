---
layout: post
title: "Provenance Techniques for CRUD"
---

Let's begin with an example and fairly common application (a blog) and a scenario of people reading a blog post and writing comments at the bottom of the page:

- Bob leaves a comment
- Sue replies to Bob's comment
- Bob edits his comment
- Bill reads Bob's comment and Sue's reply

Although this seems like a fairly harmless scenario, the issue is in the details. Let's add some times:

- `[8:20]` Bob leaves a comment
- `[8:25]` Sue replies to Bob's comment 
- `[8:29]` Bob edits his comment
- `[8:41]` Bill reads Bob's comment and Sue's reply

Depending on what Bob changed in his edit, Bill could be confused about Sue's reply. Because the context change (Bob's first version), Sue's reply may no long be relevant or may not make sense. Unfortunately, Bill is completely unaware of the change. Most good commenting citizens denote an edit has been made in the comment itself (some commenting systems automatically do this), however unless the original content is still visible, what it means and the interpretations of it will change.

We will walk through the process of capturing provenance and any data modeling and processing considerations for applying provenance techniques. Of course applying these techniques are not limited to blogs, but can be applied to any [CRUD](http://en.wikipedia.org/wiki/Create,_read,_update_and_delete)-like application (i.e. virutally any application that writes data).

The provenance concepts and terminologies introduced are from the [W3C's PROV specification](http://www.w3.org/TR/prov-overview/). The PROV specification defines provenance as:

> [the] information about entities, activities, and people involved in producing a piece of data or thing, which can be used to form assessments about its quality, reliability or trustworthiness.


### Bob leaves a comment...

There are three primary models in this example - author, post, and comment - however we are going to focus our attention on the comment. Let's assume this is how Bob's comment is represented in the data model:

```javascript
{
    "post_id": 329,
    "author_id": 49,
    "body": "...",
    "created": "2014-08-21T20:20:43Z",
    "modified": null
}
```

A create (or insert or add) operation defines something in the system that was not previously accessible. Provenance treats this *act* as an event, specifically a [generation](http://www.w3.org/TR/prov-dm/#concept-generation) event which declares the existence of an entity that is now *accessible to the rest of the world*. The generation event has a `time` attribute that marks the instantaneous time of generation and is equivalent to the `created` timestamp on the comment itself.

The generation event occurs as a result of an [activity](http://www.w3.org/TR/prov-dm/#concept-activity) that produced the comment, such as "writing and submitting the comment on the post's webpage". This may sound unnecessary, but if there is more than one way to create a comment, this information differentiates *how* the comment was created. In PROV, activities have an optional `startTime` and `endTime`. For example, if we knew when Bob began writing the comment and when he clicked the submit button, we could set these times on the activity.

A comment always has an author whether they are named or anonymous; Bob in this example. The author is referred to as an [agent](http://www.w3.org/TR/prov-dm/#concept-agent) in provenance terminology. From the PROV spec:

> An agent is something that bears some form of responsibility for an activity taking place, for the existence of an entity, or for another agent's activity.

The author is [attributed](http://www.w3.org/TR/prov-dm/#concept-attribution) to the comment and [associated](http://www.w3.org/TR/prov-dm/#concept-association) with the activity taking place. Both of these are inferred from the `author_id` attribute of the comment.

The comment did not come out of thin air. It was written based on the content and interpretation of the post. The comment was in effect *derived* from the post. PROV models this relation as a [derivation](http://www.w3.org/TR/prov-dm/#concept-derivation) and defines a derivation type [primary source](http://www.w3.org/TR/prov-dm/#concept-primary-source):

> A primary source relation is a kind of a derivation relation from secondary materials to their primary sources. It is recognized that the determination of primary sources can be up to interpretation, and should be done according to conventions accepted within the application's domain.

This translates to a comment being a secondary material derived from its primary source, the post.

To sum up all the above in a visual, this is what the provenance graph looks like for Bob's comment:

![PROV create graph](/img/prov-create1.png)

#### Summary

- The generation event denotes **when** the comment came into existence at a particular time (if available). The comment's `created` time can be used to infer the generation event.
- The activity that caused the generation event denotes **how** the comment came into existence. Although the activity is not modeled in any way in the data, it could be inferred if there is only one method for leaving a comment (web form).
- The agent specifies **who** is responsible for the activity. In this case, the comment can also be attributed to the author. The `author_id` can be used to infer responsibility and attribution of the comment.
- The comment's primary source of content or context is the post itself. The post, comment and this relation helps answer the **what** and **why**. The `post_id` can be used to infer the relation between the post and comment.

At this point it appears that most, if not all, of the provenance can be inferred from the comment data. Let us continue.

### Sue replies...

Looking back out our example, after Sue replies, Bob decides to edit his comment to clarify something or remove misinformation that Sue pointed out. A typical application would update the comment in-place and set the `modified` time:

```javascript
{
    "post_id": 329,
    "author_id": 49,
    "body": "...",
    "created": "2014-08-21T20:20:43Z",
    "modified": "2014-08-21T20:29:12Z"
}
```

The issue with an update like this, is that information is lost - specifically, the first version of Bob's comment. The downstream effect this has can be seen when Bill comes along and reads Bob's edited comment followed by Sue's reply to Bob's *original comment*. Depending on what Bob changed, Sue's reply may not make sense resulting in confusion for Bill. In a sense, the comment thread is in a corrupt state since Sue's reply is no longer associated with its *primary source*, Bob's original comment.

This type of situation is exactly why applying provenance techniques is often desired or necessary. The practical value of recording provenance is the ability to reproduce the state of an object in your application at any point in time. Modifying something removes the ability to reproduce past versions.

An important tenant when applying data provenance techniques is to treat *everything as immutable*. In practice, this means when Bob submits an edit to his original comment, a new comment is created alongside the original one. The provenance mentioned above would be captured since it is a new entity, but it has one additional relation to the original comment, known as a [revision](http://www.w3.org/TR/prov-dm/#concept-revision), which is a form of deriviation (think [version control](http://en.wikipedia.org/wiki/Revision_control)).

When an update occurs, the previous state of that comment is implicitly invalidated since it's overwritten. Since we do not modify or delete things in provenance-land, we must emulate this by recording an [invalidation](http://www.w3.org/TR/prov-dm/#concept-invalidation) event for the first comment:

> Invalidation is the start of the destruction, cessation, or expiry of an existing entity by an activity. The entity is no longer available for use (or further invalidation) after invalidation.

The provenance graph of Bob's comments now looks like this:

![PROV update graph](/img/prov-update1.png)

At first glance, this graph looks complicated, however it reflects everything that has influenced Bob's comment. Sue's comment was not included for brevity, however her comment would have a relation to Bob's original comment denoting it was derived from it in some way (e.g primary source or possibly a [quotation](http://www.w3.org/TR/prov-dm/#concept-quotation)).

#### Summary

- Modifications to a comment result in data loss and corrupts the context of any replies.
- An update/edit should create a new comment following the same provenance capture as stated above.
- A *revision* derivation between the new comment and old one is created to establish how the new one came to be. The comments themselves combined with the derivation relations represents the comment's *revision history*.
- Since we are emulating an update action, the activity used to create the new comment (submitting the web form) was also the activity that invalidated the previous comment.

#### Exercise

How would the provenance look if the *post* changes? What would happen if someone replied to Bob's comment *after* the post changed?

### Applied Provenance

Although this is a simple example, the utility of provenance can apply to every aspect of the world. To quote Wikipedia:

> [Provenance](http://en.wikipedia.org/wiki/Provenance) (from the French *provenir*, "to come from") is the chronology of the ownership, custody or location of a historical object. The term was originally mostly used in relation to works of art, but is now used in similar senses in a wide range of fields, including archaeology, paleontology, archives, manuscripts, printed books, and science and computing.

In the clinical research and healthcare fields (where I work), provenance is essential due to the breadth and variability of domains and data formats. Much of healthcare data is free-text or in formats that require heavy processing before being used in secondary applications. Data processing increases the likelihood of error and descreases its certainy at every (non-trivial) step unless it is known how the data was derived from its source.

Putting in the effort to apply these simple techniques to your applications or processes will increase the trustworthiness, reliability, and overall quality of the data.

---

*[Discuss on Hacker News](https://news.ycombinator.com/item?id=8212476)*
