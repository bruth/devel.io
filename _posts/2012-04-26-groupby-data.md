---
layout: post
title: Group Your Data
---

Working in a research hospital made me realize something. Tabular data can be confusing as hell.

Each row provides a false sense of reality. Most people can only process a single row at a time, yet the tabular format, I would argue, is the most prevelant data format in existence. It's easy to parse and relatively easy to scan down columns.

```
a	b	c	d	e
-	-	-	-	-
1	1	0	2	3
1	0	2	2	2
2	2	2	0	0
3	1	2	3	3
3	0	2	0	1
```

But scanning columns isn't enough. If it were, each column could be aggregated with the count of each distinct value.

```
c	#	
-	-
0	1
2	4
```

What most people attempt to do is simultaneously scan the rows for each batch, let's say relative to column `a`, and look at the data only for that batch.

```
a	b	c	d	e
-	-	-	-	-
1	1	0	2	3
1	0	2	2	2

2	2	2	0	0

3	1	2	3	3
3	0	2	0	1
```

This is very prone to error and takes up quite a bit of time to process for any sized table.

Tabular data should be grouped. For each column that is used for the grouping, it should be removed from the table.

**Grouped by `a`**

```
	b	c	d	e
	-	-	-	-
1	1	0	2	3
	0	2	2	2

2	2	2	0	0

3	1	2	3	3
	0	2	0	1
```

**Grouped by `c`**

```
	a	b	d	e
	-	-	-	-
0	1	1	2	3

2	1	0	2	2
	2	2	0	0
	3	1	3	3
	3	0	0	1
```

**Grouped by `c` and `d`**

```
		a	b	e
		-	-	-
0,2		1	1	3

2,0		3	0	1
		2	2	0
2,2		1	0	2
2,3		3	1	3
```

My point? If you're presenting tabular data, do the world a favor and create groups where appropriate.