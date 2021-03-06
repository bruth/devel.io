---
published: true
layout: post
title: "Notes: The Little MongoDB Book"
summary: Personal notes from reading [The Little MongoDB Book](http://openmymind.net/2011/3/28/The-Little-MongoDB-Book/) by Karl Seguin with additional thoughts and comments.
---

### Schemas

- Most of [schema](http://en.wikipedia.org/wiki/Database_schema) vs. schemaless arguments boil down to whether the database system _requires_ a predefined schema
- Data that _is_ schemaless can be difficult to work with since you don't _know_ what the structure is and therefore cannot easily work with it
- Just because Mongo is schemaless doesn't mean you should shove highly mismatched data in the same collection

#### Flexibility

- Every document in a single collection _could_ be different
- Collections are _dumb_ since each document holds the information about it's own _schema_
	- This also comes with a lot of redundancy in a collection is _regular_
- Databases and collections are created _on-the-fly_ which makes it simple for automatic loading of random bits of data from different sources
	- Which them could be consolidated later

### Writes

- Waiting for writes to complete can be customized per query depending on need for integrity of the data
	- Fire-and-forget writes can be followed by `db.getLastError()` to return the error if present
    	- Most drivers wrap this behavior and call it a _safe_ write

#### Transactions

- Built-in modifiers like `$set` are atomic as well as the `findAndModify()`
- Two-phase commits are also common to emulate transactions
	- The state of the transaction is stored in the document itself being updated and the init-pending-commit/rollback steps are applied manually

### Terminology

- **database** - Exist within a Mongo instance.
- **collection** - Exist within a database and are conceptually equivalent to tables in a relational database.
- **document** - Exist within a collection and are conceptually equivalent to rows in a relational database.
- **field** - Defined on a document and are conceptually equivalent to columns in a relational database.
- **index** - Defined on collections and are conceptually equivalent to indexes in a relational database.
- **cursor** - Primary interface to the data. This is the same as with relational database drivers.

### Use Cases

- Storage for _longer_-term cache when something like [memcached](memcached.org) is too volatile or data structures are needed
- Intermediate or staging storage for [ETL](http://en.wikipedia.org/wiki/Extract,_transform,_load)
- Alternate to RMDBS

### Details/Concepts

- **No joins**, premise: they don't scale in a general way, application must handle the logic
- BSON is the internal storage format, JSON is the API layer format
- `db.system.indexes` is created (implicitly) once per database to store information about indexes
- Every document has a `_id` field generated if one is not supplied
- The `_id` field is indexed per collection
- Maximum document size is 16MB
	- Let this be a hard constraint that drives data modeling decisions

### Data Modeling

- "To embed or not to embed, that is the question"
- Related data can exist in separate collections
	- Requires multiple queries to access everything
- Related data is embeddeMultiple queries for related objects vs. embedded related data (which is a tad less accessible)
- Storage considerations http://docs.mongodb.org/manual/faq/storage/
	- Have enough RAM to fit the _working set_, otherwise hard page faults will occur

#### DBRef

- This has been somewhat formalized due to convention by many drivers
- Document signature: `{$ref: <collection name>, $id, <doc id>, $db, <database name>}` (oddly, the fields must be defined in this order as well)
	- The `$db` field is optional and also not supported by all drivers
- More details - http://docs.mongodb.org/manual/reference/database-references/

#### Collections

- Collections are created implicitly the first time they are accessed
- Capped collections can be created using `db.createCollection(...)` either by size in bytes or number of documents
	- `db.createCollection(<name>, {capped: true, [size: <bytes>], [max: <count>]})`

### Selectors

- Similiar to the `WHERE` clause in SQL
- Arrays are traversed implicitly, i.e. `{email: 'foo@example.com'}` will match on both `{email: 'foo@example.com'}` and `{email: ['foo@example.com', 'bar@example.com']}`
- Dot-notation is used for accessing embedded documents, e.g. `'user.profile.email'`
- Selectors are specified as JavaScript objects themselves, e.g. `{age: {$gt: 10}}`
- `{}` selector matches all documents
- Few common ones
	- exact match does not use an operator, e.g. `{middle_name: 'James'}`
    - `$ne` - not equal
	- `$exists` - presence/absence of a field, e.g. `{middle_name: {$exists: true}}`
    - `$lt`, `$lte`, `$gt`, `$gte` - numerical operators
    - `$or` - groups conditions for a logical OR rather than AND, e.g. `{$or: [{$color: 'blue'}, {$color: 'red'}]}`
- Most flexible one is `$where` in which a function can be supplied to filter results

### Indexes

- Signature: `db.collection.ensureIndex(<fields>, <options>)`
	- The `options` param can contain `{unique: true}` to create a unique index
- Indexes can be created on embedded documents
- Use `dropIndex(<fields>)`
- Indexes can be created in ascending or descending order
	- This only impacts compound indexes, i.e. the relationship between the keys
- Use `cursor.explain()` to see if indexes are being used and general stats
	- `BasicCursor` means no indexes were not used, while `BtreeCursor` implies an index was used

### Core Methods

#### Find

- Signature: `db.collection.find(<selector>, <projection>)`
- The `projection` decides which fields to return by the cursor
	- `db.users.find({contact: true}, {name: 1, email: 1})` returns all names and email addresses for those who want to be contacted
    - The `_id` is always returned unless the projection disables it explicitly, i.e. `{_id: 0}`

#### Sort

- Signature: `cursor.sort(<ordering>)`
- The `ordering` document contains field names with `1` for ascending or `-1` for descending, e.g. `db.users.find().sort({dob: -1})` for the oldest users first

#### Limit

- Signature: `cursor.limit(<int>)`
- Limit the documents being fetched

#### Skip

- Signature: `cursor.skip(<int>)`
- Skip the first N documents

#### Count

- Signature: `cursor.count()` or directly on the collection: `db.collection.count()`

#### Update

- Signature: `db.collection.update(<selector>, <document>, <upsert>, <multiple>)`
- Modifiers are atomic as well as the `findAndModify()` function
- Default behavior is to _replace_ matched documents
- Use the `$set` modifier to update individual attributes, `{$set: {color: 'Blue'}}` rather than `{color: 'Blue'}`
- Other modifiers
	- `$inc` - adds the value to a number (positive or negative)
    - `$push` - appends a new value/document to an array
- Set `upsert` to true to create the document being updated if it doesn't exist
	- Useful for counters, `db.foo.update({name: 'counter x'}, {$inc: {count: 1}}, true)` which find or create the document `{name: 'counter x'}` and increment `count` by one. If the document is new, the value will be incremented from 0
    - Creating lists on the fly, `db.foo.update({name: 'colors'}, {$push, {values: 'blue'}}, true)` will find or create the document `{name: 'colors'}` and append `'blue'` to `values`. If the document is new, `values` will be initialized as an empty array prior to the push.
- By defaults, `update(...)` affect at most one document (the first one found) unless the `multiple` argument is `true`

### MapReduce

- Signature: `db.collection.mapReduce(<map>, <reduce>, <options>)`
	- `options` can be `{out: {inline: 1}}` for data to be streamed back (limited to 16MB) or `{out: <collection>}` to be inserted into a collection
    - Data outputed to a collection will replace existing data unless `{out: {merge: <collection>}}` is used in which case values for the same keys will be replaced and new keys will be inserted
    - The _actual_ ouput documents are `{_id: <key>, value: <value>}` to conform with the standard document structure
    - Other options can be seen here: http://docs.mongodb.org/manual/reference/command/mapReduce/
- Map functions emit 0 or more (key, value) pairs
- Keys can be complex objects
- Within a map function, `this` refers to the current document being handled
- Reduce functions take a key and array of values and emit the aggregation

### Geospatial

- Store coordinates `x` and `y` with a geospatial index which supports the `$near` and `$within` operators
- Details: http://docs.mongodb.org/manual/core/geospatial-indexes/

### Tools

- `db.stats()` or `db.collection.stats()` for information on the respective components
- locahost:28017 to access the MongoDB web interface
	- Add `rest=true` to the config to expose a RESTful API
- Profiling can be turned on by doing setting setting a profiling level greater than 0, e.g. `db.setProfilingLevel(2, <ms>)
	- 1 - profile queries that take more than 100 milliseconds (by default) or whatever `<ms>` is set to
    - 2 - profile everything
- Use the `mongodump` and `mongorestore` for backup and restore
- Use `mongoexport` and `mongoimport` for exporting and importing to/from JSON and CSV

### References

- [The Little MongoDB Book](http://openmymind.net/2011/3/28/The-Little-MongoDB-Book/) by Karl Seguin
- [MongoDB Manual](http://docs.mongodb.org/manual/) (of course)
- [MongoDB Reference Cards](http://www.mongodb.com/reference)
- [MongoDB Presentations](http://www.mongodb.com/presentations)
