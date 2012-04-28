---
layout: post
title: Group Your Data - Take Two
---

Following up my [previous post on Grouping Your Data]({% post_url 2012-04-26-groupby-data %}),
here is a more concrete example. I wrote two simple functions for grouping the data
and then generating the HTML.

- [sortedGroupBy](https://gist.github.com/2504688) - It is a light wrapper around
[Underscore's groupby function](http://underscorejs.org#groupBy)
- [groupByHtml](https://gist.github.com/2505302) - It uses a simple function to
generate the HTML given the resulting data from the first function.

<style>
#controls {
  border-radius: 3px;
  background-color: #fff;
  padding: 20px;
  margin-right: 20px;
  vertical-align: top;
}
#example, #controls {
  display: inline-block; }
.group {
  margin-bottom: 10px; }
.group > * {
  display: inline-block;
  vertical-align: middle; }
.group .group-label {
  padding: 5px 10px;
  font-size: 18px;
  font-weight: bold; }
.group .group-label .group-key {
  display: block;
  margin-right: 5px; }
.group .group-table {
  width: auto;
  background-color: #fff;
  border-radius: 3px;
  border-collapse: collapse; }
.group .group-table td, .group .group-table th {
  border: 1px solid #ddd;
  padding: 5px; }
.group .group-table th {
  background-color: #eee; }
</style>

<div id=controls>
    <strong>Group by..</strong><br>
    <label><input class=column type=checkbox name=genre> Genre</label><br>
    <label><input class=column type=checkbox name=price> Price</label><br>
    <label><input class=column type=checkbox name=status> Status</label>
</div>

<div id=example></div>

<script src=http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js></script>
<script src=http://documentcloud.github.com/underscore/underscore-min.js></script>
<script>
    var movies = [{
        title: "Office Space",
        released: "1999-02-19",
        genre: "Comedy",
        price: 19.95,
        status: "Available"
    },{
        title: "Super Troopers",
        released: "2002-02-15",
        genre: "Comedy",
        price: 14.95,
        status: "Unavailable"
    },{
        title: "American Beauty",
        released: "1999-10-01",
        genre: "Drama",
        price: 19.95,
        status: "Available"
    },{
        title: "The Big Lebowski",
        released: "1998-03-06",
        genre: "Comedy",
        price: 21.90,
        status: "Available"
    },{
        title: "Fight Club",
        released: "1999-10-15",
        genre: "Drama",
        price:  19.95,
        status: "Available"
    }];

    function sortedGroupBy(list, groupByIter, sortByIter) {
        if (_.isArray(groupByIter)) {
            function groupBy(obj) {
                return _.map(groupByIter, function(key, value) {
                    return obj[key];
                });
            }
        } else {
            var groupBy = groupByIter;
        }
        if (_.isArray(sortByIter)) {
            function sortBy(obj) {
                return _.map(sortByIter, function(key, value) {
                    return obj[key];
                });
            }
        } else {
            var sortBy = sortByIter;
        }
        var groups = _.groupBy(list, groupBy);
        _.each(groups, function(value, key, list) {
            list[key] = _.sortBy(value, sortBy);
        });
        return groups;
    }

    function groupByHtml(groups, keys, sep) {
        var html = [],
            sep = sep || ',';
        // Build group
        _.each(groups, function(list, groupKey) {
            var group = $('<div>').addClass('group'),
                label = $('<span>').addClass('group-label'),
                table = $('<table>').addClass('group-table'),
                header = $('<tr>'),
                tbody = $('<tbody>');
            if (_.isString(groupKey)) {
                _.each(groupKey.split(sep), function(tok) {
                    label.append('<span class=group-key>' + $.trim(tok) + '</span>');
                });
            } else {
                label.append('<span class=group-key>' + groupKey + '</span>');
            }
            // Build table
            _.each(list, function(obj, i) {
                var tr = $('<tr>');
                _.each(obj, function(value, key) {
                    // Add group label on first iteration
                    if (keys.indexOf(key) >= 0) {
                        if (i == 0) {
                            
                        }
                    } else {
                        // Add head row on first iteration
                        if (i == 0) {
                            header.append('<th>' + key + '</th>');
                        }
                        tr.append('<td>' + value + '</td>');
                    }
                });
                tbody.append(tr);
            });
            $('<thead>').appendTo(table).append(header);
            table.append(tbody);    
            group.append(label, table);
            html.push(group);
        });
        return html;
    }

    $(function() {
        var example = $('#example'),
            columns = $('.column');

        function regroup() {
            var cols = [];
            $.each(columns, function(i, e) {
                if ($(e).prop('checked')) {
                    cols.push($(e).attr('name'));
                }
            });

            var groups = sortedGroupBy(movies, cols);
            example.empty().append.apply(example, groupByHtml(groups, cols));
        }

        columns.on('click', regroup);
        regroup();
    });
</script>
