---
layout: post
title: Designing for Metadata-driven Data Discovery
---

What is necessary for taking _data about data_ and using it to drive data discovery?

**Context.**

## Understanding Metadata

When attempting to explain what metadata is, most people typically bob their heads in agreement and crack the joke, "we have metadata coming out of our metadata!".

I find this somewhat humorless because this means the person has no idea what you are talking about. Metadata, by definition, has an elusive meaning because it's meaning depends on the context of what you are talking about. The formal definition does not provide much help.

> A set of data that describes and gives information about other data.

The [Metadata entry on Wikipedia](http://en.wikipedia.org/wiki/Metadata) attempts to disambiguate the meaning and provides much more detail. The two types of metadata described are **structural metadata**, data about the containers of data, and **descriptive metadata**, data about data content.

We will come back to these definitions.

## Start With The Data

As an example, let's look at some made-up data about apples.

```
name				cost	color	firmness
----				----	-----	--------
red delicious		0.30	red		medium
golden delicious	0.30	gold	null
granny smith		0.40	green	hard
gala				0.40	mixed	medium
rome				0.70	red		null
fuji				0.60	mixed	medium
```

What metadata can you extract from this data?

#### name

- the `name` is unique
- the data itself is composed of alpha characters

#### cost (per apple)

- the `cost` is a number, but more precisely corresponds to the U.S. currency, thus constraining it to two decimal places and cannot be negative
- the cost has an lower bound of $0.30 and an upper bound of $0.70

#### color

- the `color` is not unique
- like the `name`, color is composed of alpha characters

#### firmness

- the `firmness` is not unique
- some apples have an unknown firmness (denoted by `null`)
- the data is composed of alpha characters

## Progression of Context

Structural metadata adds constraints to the types of queries (questions) you can make about the data. Obviously asking the question  _"give me all the apples with a cost of 'water'"_ doesn't make any sense. The fact that we know the `cost` is a currency allows us to validate the query prior to executing it.

Validation is hugely important, but no one _sees_ validation. The same metadata used for the validation rules can be applied when building an interface for building queries. Using the `cost` data as an example, an HTML form could be used to represent a currency input such as (the HTML input attribute `placeholder` is used here to show an example value):

<strong>Apple cost - <input name=cost placeholder="50"> cents</strong>

---

Likewise, the available _operators_ that can be used with the value can also be derived from the fact that it's a numerical value.

<strong>
	Apple cost
	<select name=cost-operator>
	<option value=exact>is equal to</option>
	<option value=gt>is greater than</option>
	<option value=lt>is less than</option>
	</select>
	<input name=cost placeholder="50"> cents
</strong>

---

With respect to the non-numerical data, a form build to represent the available colors could simply be a drop-down.

<strong>Apple color -
	<select name=color>
		<option>---</option>
		<option value=red>Red</option>
		<option value=green>Green</option>
		<option value=gold>Gold</option>
		<option value=mixed>Mixed</option>
	</select>
</strong>

---

_**Quick Note on Validation** Validation is only really necessary when dealing with free-text input. If your enumerated lists have been generated from your data, then it is already valid. But for example, the `cost` input box above still technically allows for any character to be entered. Performing a simple validation ensures immediate feedback to the end-user that they have made a mistake and prevents building and executing an invalid query._

## Input Processing Steps

### Parse raw input
This is more of pre-processing step that ensures the input data structure is in a valid format that can be understood by the following steps. A simple JSON structure that represents a query condition may look like this:

```javascript
{
	"id": "apple.color",
	"operator": "equals",
	"value": "red"
}
```

If these three data are not present, downstream cannot occur.

_One other thing to consider is the relationship between query conditions. If the downstream datastore (such as a relational database) can handle nested expressions, processing in this step and downstream may need to be recursive._

### Validate and clean
As mentioned above, validation is necessary for any kind of input that was not derived from the data itself. The above code provides the data necessary for performing validation.

Cleaning is optional depending on the source of the data. If data has been fed into the system via some other means that does not map to native datatypes, cleaning can be performed to coerce the raw input into some native data structure. Given the following raw input:

```javascript
{
	"id": "apple.cost",
	"operator": "greater than",
	"value": "0.40"
}
```

The value of `"0.40"` is a technically a number, but it is represented as a string in this particular serialization format. A simply cleaning step can attempt to coerce the string into a native number.

### Input Translation

This step is optional, but in certain cases the input data may not cleanly map to the stored data. In the **Apple cost** form field examples above, a keen eye may have noticed the units displayed was _cents_, not _dollars_, but the data is stored relative to dollars. Assuming a client like the above did exist (which is a bit silly), a translator could be defined to take an input value of `40` cents and divide it by `100` to convert it into the dollar unit.

```javascript
function cents_to_dollars(value) {
	return value / 100.0;
}
```

_In this example the `40` cents is just a number from the query engine's standpoint. It doesn't know the units is in cents and would just assume the value as `40.00` dollars. The engine does not (and should not) know how the client is presenting interface for input, so it is important that the client performs any translation itself prior to passing it off to the query engine._

### Query Building

Now that the input data is valid and cleaned, it must be converted into it's appropriate syntax for the end datastore. For example, if the datastore is a relational database, a SQL statement must be generated in order to perform a query. This step is backend dependent, but assuming each backend has support for the abstractions above, the code necessary for this step can be written with an abstraction layer for convenience.

Using SQL as the output, the following input...

```javascript
{
	"id": "apple.cost",
	"operator": "greater than",
	"value": "0.40"
}
```

...would result in this output. _The asterisk (*) is being used in the `SELECT` portion for now until it is discussed how to specifiy which data to be retrieved using metadata in a similar (but less complex) manner as above in an upcoming article._

```sql
SELECT * FROM apples WHERE cost > 0.40
```

Or with a nested input structure:

```javascript
{
	"type": "and",
	"children": [{
		"id": "apple.cost",
		"operator": "greater than",
		"value": "0.40"
	}, {
		"id": "apple.color",
		"operator": "equals",
		"value": "red"
	}]
}
```
...and the resulting SQL:

```sql
SELECT * FROM apples WHERE cost > 0.40 AND color = 'red'
```
