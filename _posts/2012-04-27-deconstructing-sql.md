---
layout: post
title: Deconstructing SQL
---

What's in a SQL query?

```sql
SELECT *
    FROM book
    WHERE price > 15.00
    ORDER BY title;
```

A SQL `SELECT` query is composed of several components, but I won't introduce them in the order they appear in a query because I believe it's a backwards way of thinking.

## Conditions

The first I think about when writing a SQL query is what data my question ultimately applies to. For example, in the query above the expression `price > 15.00` removes all books that cost $15.00 or less. Of course multiple conditions can be provided to slice up the data in any way.

```sql
... WHERE price < 10.0 OR price > 100.00
```

The `WHERE` clause defines the conditions that are used to filter the data. 
Conditions most commonly act on each row individually. That is, the statement `price < 10.0 AND price > 100.0` will test the `price` in each row and remove the rows that don't pass.

## Aggregations

An aggregation is composed of one or more aggregate functions to be applied to the table rows.

#### Count the number of books

```sql
SELECT COUNT(*) FROM book
```

#### Calculate the average price of all books

```sql
SELECT AVG(price) FROM book
```

#### Multiple aggregation calculations

```sql
SELECT MIN(price), MAX(price), AVG(price) FROM book
```
Using aggregate functions like this will always return a single row.

_As an aside, most database engines will throw an error if a non-aggregated value is added to the `SELECT` caluse, for example `SELECT price, AVG(price) FROM book`. SQLite will gladly return an arbitrary value for that `price` column._

### GROUP BY

As the name suggests, the `GROUP BY` clause enables grouping rows by value. The simple thing to remember is that any columns that appear in the `GROUP BY` must also appear in the `SELECT` clause.

#### Group rows by genre

```sql
SELECT genre
	FROM book
	GROUP BY genre
```

The above query returns one row per `genre`. Multiple columns can be added to group rows by each combination of values.

#### Group rows by genre and author

```sql
SELECT genre, author
	FROM book
	GROUP BY genre, author
```

_An aside, there is a shortcut available to the `GROUP BY` statements above using the `SELECT DISTINCT`_

#### Select distinct values

```sql
SELECT DISTINCT genre, author FROM book
```

### GROUP BY Aggregations

Typically the `GROUP BY` clause is used with aggregate functions. The aggregate functions are effectively applied to each group individually.

#### Count of books per genre

```sql
SELECT genre, COUNT(*)
	FROM book
	GROUP BY genre
```


#### Average price of book per genre

```sql
SELECT genre, AVG(price)
	FROM book
	GROUP BY genre
```

It is common to ask questions about aggregate calculations. One might think these conditions could just be throw in the `WHERE` clause with the others, but there is a separate clause called `HAVING` for this.

#### Average price of book per genre above $10

```sql
SELECT genre, AVG(price)
	FROM book
	GROUP BY genre
	HAVING AVG(price) > 10.0
```

_Note, the `AVG(price)` in the `SELECT` clause is not required, but included because it is typically desired to have the calculated averages in the result._

The reason is being the `GROUP BY` is applied _after_ the data has been filtered by the `WHERE` clause. Likewise, the `HAVING` clause is applied after the `GROUP BY` clause. Again this is because the aggregate calculations apply after each group has been defined, and then the those aggregated rows will be filter further by the `HAVING` clause.

#### Genres with more than 100 books within the $10-$20 price range

```sql
SELECT genre, COUNT(*)
	FROM book
	WHERE price BETWEEN 10 AND 20
	GROUP BY genre
	HAVING COUNT(*) > 100
```

## And now... SELECT

I purposefully deferred talking about the `SELECT` clause until now because I believe it is important to think about the constraints of a question before worrying about what data you actually want to view.

As stated above, the only real constraint with what must be in the `SELECT` clause are the columns that are declared in the `GROUP BY` clause and vice versa (excluding aggregate functions of course).

Expressions can also be used to return a representation of the data.

```sql
SELECT price, (price * 0.08) AS tax FROM book
```

_Note, parentheses were added for visual clarity. They are typically not required._

## Next Steps

This text by no means covers the totality of the Structred Query Language (SQL), but rather presents a way of thinking when attempting to write a query. I have gotten caught up many a time when attempting to deconstruct a natural language question and writing in SQL.

The one topic I left out is regarding table joins. I did this because it can be overwhelming to think about since the number of columns and rows may grow expontentially depending on the type of join.

Again, the way to think about joins is that you are effectively starting with a larger table. When you perform a join, you are effectivaly annotating one table with the data from another. As a quick example:

#### Count the books per author

```sql
SELECT author.name, COUNT(*)
	FROM book, author
	WHERE book.author_id = author.id
	GROUP BY author.name
```

The join in the above query produces a table that looks like this (the redundant `id` columns are the primary keys of each table):

```
id	title	price	genre	author_id	id	name
--	-----	-----	-----	---------	--	----
```

Once the table is constructed (from the database engine's point-of-view) the rest of the query components will be applied as expected.