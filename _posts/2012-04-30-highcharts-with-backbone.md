---
layout: post
title: Highcharts with Backbone
summary: Simplify creating JavaScript rendered charts using [Backbone](http://backbonejs.org) and [Highcharts](http://www.highcharts.com).

---

[Highcharts](http://www.highcharts.com/) is a pretty excellent charting library. It has a [plethora of configuration options](http://www.highcharts.com/ref/) which is great for customization, but is quite daunting for simple charts. I will applying some [convention over configuration](http://en.wikipedia.org/wiki/Convention_over_configuration) in the examples below mainly to keep things simple.

I use [Backbone](http://backbonejs.org) for many things on the client since I see it as a general purpose tool for structuring your client-side apps (along with AMD modules). The simple idea here is to create Backbone `View` subclasses representing a the chart types. The data source will of course be a Backbone `Model` or `Collection` which keeps things cleanly abstracted.

Let's start with the data.

## DataPoint and Series

Having specific classes provides the most flexibility in terms of customizing the options for a given series and/or data point. Highcharts provides a lot of flexibility in how [series](http://www.highcharts.com/ref/#series) and [data points](http://www.highcharts.com/ref/#point) are defined and customized. Each series can be customized independently which may make having formal classes desirable.

```coffeescript
# Nothing special, just a subclass for the naming convenience
class DataPoint extends Backbone.Model

# To get the full series options, the toJSON method can be changed to
# nest the data points
class Series extends Backbone.Collection
	model: DataPoint
	
	initialize: (options) ->
		# Other series options may be passed in
		@options = options

	# Override to nest the data points
	toJSON: ->
		options = _.clone @options
		# Nest the data points to match the Highcharts options
		options.data = super
		return options


# Assuming the model attributes match the Highcharts point options
# calling the toJSON method would be good enough
model = new DataPoint x: 1, y: 20

# Produces { x: 1, y: 20 } which can be used directly in the
# series data array
point = model.toJSON()

# Create a collection with some data points
collection = new Series [...]

# Using Series, the toJSON method will produces options ready to be
# added the chart's series array
series = collection.toJSON()
```

This provides the greatest flexibility for customization, but the potential overhead for having a model instance for every data point may not make this feasible. _TODO do a perf and memory test to measure this.. then write it up =)_

To reduce the memory or need for configuration, the `Series` class could be a `Model` subclass instead. The options and data would be stored as-is.

Now let's look how to hook it up to a view.

## Base Chart View

Chart options only differ very slightly between chart types (e.g. bar, line, scatter), thus we should start with a base view the encapsulates the default options and attach the view's element to the `chart.renderTo` option.

```coffeescript
class Chart extends Backbone.View
	defaultOptions:
		chart: {}
	
	initialize: (options) ->
		@options = $.extend true, {}, @defaultOptions, options
		@options.chart.renderTo = @el

	render: ->
		# Destroy previous chart
		if @chart then @chart.destroy()

		# Assume model-based series
		if @model
			@options.series = [@model.toJSON()]
		# There are two potential usages of a collection. If the collection
		# is a Series instance (as defined above), treat it as a single
		# series. Otherwise assume it is a collection of multiple series
		else if @collection
			if @collection instanceof Series
				@options.series = [@collection.toJSON()]
			else
				@options.series = @collection.toJSON()

		@chart = new Highcharts.Chart @options
		return @
```

The above provides the bare minimum in terms of rendering a chart given the `model` or `collection`, but currently, if the data changes there the chart will not update.

Highcharts provides various [chart methods](http://www.highcharts.com/ref/#chart-object) and [series methods](http://www.highcharts.com/ref/#series-object) for altering the data in the chart and redrawing the chart at will. We can take advantage of the Backbone events to known when this happens.

```coffeescript
class DynamicChart extends Chart

	initialize: (options) ->
		super options
		# Bind to collection or model events for knowing when to redraw the chart
		if @collection
			if @collection instanceof Series
				@collection.on 'add', @addPoint
			else
				@collection.on 'add', @addSeries

	addPoint: (collection, model, options) =>
		if not @chart then return
		idx = collection.indexOf model
		@chart.series[idx].addPoint model.toJSON()

	addSeries: (collection, model, options) =>
		if not @chart then return
		@chart.addSeries model.toJSON()
```

## Chart Subclasses

For convenience and readability, we can define subclasses for the supported chart types, with their respective default options in case there are subtle differences with the layout or colors.

```coffeescript
class AreaChart extends Chart
	defaultOptions:
		chart:
			type: 'area'
	
class AreaSplineChart extends Chart
	defaultOptions:
		chart:
			type: 'areaspline'

class BarChart extends Chart
	defaultOptions:
		chart:
			type: 'bar'

class ColumnChart extends Chart
	defaultOptions:
		chart:
			type: 'column'

class LineChart extends Chart
	defaultOptions:
		chart:
			type: 'line'

class PieChart extends Chart
	defaultOptions:
		chart:
			type: 'pie'

class ScatterChart extends Chart
	defaultOptions:
		chart:
			type: 'scatter'

class SplineChart extends Chart
	defaultOptions:
		chart:
			type: 'spline'
```

This is only the beginning. There are a few other conveniences that can be implemented, such as:

- passing in view options that map to some nested Highcharts configuration
- the ability to pass data directly to the view for one-off charts (no need for a `Model` or `Collection`)
- data parsers that return structures compatible with Highcarts

I will be making a library with this boilerplate code. Stay tuned for an upcoming post!
