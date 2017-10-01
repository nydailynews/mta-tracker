//**TODO add a countdown that lets a reader know how long until the next check for updates
var tracker = {
    d: {},
    now: Date.now(),
    tz_offset: -6,
    rando: function()
    {
        // Generate a random ascii string, useful for busting caches.
        var text = "";
        var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

        for( var i=0; i < 20; i++ )
            text += possible.charAt(Math.floor(Math.random() * possible.length));

        return text;
    },
    calc_time_zone: function(offset) {
        // Get the current time in a different timezone. Must know the tz offset,
        // i.e. the number of hours ahead or behind GMT.
        var d = new Date();
        var utc = d.getTime() - (d.getTimezoneOffset() * 60000);
        return new Date(utc + (3600000*offset));
    },
    add_zero: function(i) {
        // For values less than 10, return a zero-prefixed version of that value.
        if ( i < 10 ) return "0" + i;
        return i;
    },
    count_up: function() {
        // Handle the parsing and passage of time.
        // Loop through each of the <time> elements on the page and update them.
        var times = document.querySelector('time');
        $('time').each( function(i) {
            var time = $(this).text();
            var time_parts = time.split(':');
            if ( time_parts.length == 3 ) var secs = +time_parts[2], mins = +time_parts[1], hours = +time_parts[0];
            if ( time_parts.length == 2 ) var secs = +time_parts[1], mins = +time_parts[0], hours = 0;
            secs += 1;
            if ( secs > 59 )
            {
                secs = 0;
                mins += 1;
                if ( mins > 59 )
                {
                    mins = 0;
                    hours += 1;
                }
            }
            if ( hours > 0 ) time = hours + ':' + tracker.add_zero(mins) + ':' + tracker.add_zero(secs);
            else time = tracker.add_zero(mins) + ':' + tracker.add_zero(secs);
            $(this).text(time);
        });
    },
    calc_time_since: function(time) {
        // time is a datetime-looking string such as "2017-07-25 11:32:00"
        if ( time <= 0 ) return 0;
        //console.log(time);
        var t = time.replace(' ', 'T');
        //var t = time
        window.t = Date.parse(t)
        //var t = time.replace(' ', 'T') + "-0400";
        //console.log(time, Date.parse(t), t);
        return Math.floor((Date.now() - Date.parse(t))/1000);
    },
    convert_seconds: function(sec) {
        // Turns an integer into the representative number of minutes and hours.
        var hours = Math.floor(sec/3600);
        var minutes = Math.floor((sec-hours*3600)/60);
        var secs = sec%60;
        if ( minutes < 10 ) minutes = "0" + minutes;
        if ( secs < 10 ) secs = "0" + secs;
        if ( hours > 0 ) return hours + ':' + minutes + ':' + secs;
        return minutes + ':' + secs;
    },
    update_timer: function(id, value) {
        document.getElementById(id).innerHTML = value;
    },
    lines: {
        subway: {
            worsts: []
        }
    },
    get_line_data: function(key, value) {
        // loop through the data object until an item's key matches its value.
        var l = this.d.current.length;
        for ( var i = 0; i < l; i ++ ) {
            if ( this.d.current[i][key] == value ) return this.d.current[i];
        }
    },
    update_recent: function() {
        // Write the list of recent alerts
        shown = 0;
        Array.prototype.forEach.call(this.sorted, function(item, i) {
            var l = item['line'];
            if ( l == 'ALL' ) return false;
            if ( tracker.lines.subway.worsts.indexOf(l) > -1 ) return false;
            shown += 1;
            if ( item['ago'] > 100332086 ) return false;

            var markup = '<dt><img src="static/img/line_' + l + '.png" alt="MTA ' + l + ' line icon"></dt>\n\
                <dd><time id="line-' + l + '">' + tracker.convert_seconds(item['ago']) + '</time> since the last alert</dd>';
            $('#recent dl').append(markup);
        });
        w = window.setInterval("tracker.count_up()", 1000);
    },
    update_lead_no_alert: function() {
        // Write the lead and start the timer.
        // The worst time will be the first item in the sorted array
        //$('#lead h1').text('MTA Tracker');
        this.update_timer('yes-no', 'NO');
        this.update_timer('timer-text', this.convert_seconds(this.sorted[0]['ago']));
        // Update the p text
        var s = '', were = 'was';
        if ( this.lines.subway.worsts.length > 1 ) {
            s = 's';
            were = 'were';
        }
        //$('#lead p').text('since the last MTA subway service alert.');
        $('#lead p').after('<p>Latest service alert' + s + ' ' + were + ' for the ' + this.lines.subway.worsts.join(' and ') + '&nbsp;line' + s + '.</p>');
    },
    parse_cause: function(value) {
        return value;
    },
    slugify: function (text) {
        // from https://gist.github.com/mathewbyrne/1280286
        return text.toString().toLowerCase()
            .replace(/\s+/g, '-')           // Replace spaces with -
            .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
            .replace(/\-\-+/g, '-')         // Replace multiple - with single -
            .replace(/^-+/, '')             // Trim - from start of text
            .replace(/-+$/, '');            // Trim - from end of text
    },
    update_lead_alert: function() {
        // Write the lead text and timer.
        $('#lead h1').text('Is there a current MTA service alert?');
        this.update_timer('yes-no', 'YES');
        // Update the paragraph
        var s = '';
        var end_of_graf = ': ' + this.get_line_data("line", this.lines.subway.worsts[0]).cause;
        var len = this.lines.subway.worsts.length;

        // If there are multiple delays we list them in a dl
        // If any of the delay causes are identical we group them.
        if ( len > 1 ) {
            end_of_graf = ':';
            s = 's';

            // First we see how many distinct causes there are.
            var causes = [];
            var groups = {};
            var is_multiple = 0;
            var multiples = [];
            for ( var i = 0; i < len; i ++ ) {
                var l = this.lines.subway.worsts[i];
                var cause = this.get_line_data("line", l).cause;
                if ( causes.indexOf(cause) === -1 ) {
                    // Add the cause to the list of causes
                    // so we know if the next cause is new or not.
                    causes.push(this.get_line_data("line", l).cause);
                    // Also associate the line with the cause so we can later
                    // put all/any lines with the same cause together.
                    groups[cause] = [l];
                }
                else {
                    // We have a duplicate cause
                    is_multiple = 1;
                    // We want to know which cause(s) are multiples.
                    multiples.push(cause);
                    groups[cause].push(l);
                }
            }

            // Next we generate and place the markup
            for ( var i = 0; i < len; i ++ ) {
                var l = this.lines.subway.worsts[i];
                var record = this.get_line_data("line", l);
                var img = '<img src="static/img/line_' + l + '.png" alt="MTA ' + l + ' line icon">';

                if ( record.cause.indexOf(' *** ') >= 0 ) {
                    var causes = record.cause.split(' *** ')
                    var jlen = causes.length;
                    for ( var j = 0; j < jlen; j ++ ) {
                        var slug = this.slugify(causes[j]);
                        var dt = $('#' + slug);
                        if ( dt.length ) {
                            dt.append(img);
                        }
                        else {
                            var markup = '<dt id="' + slug + '">' + img + '</dt><dd>' + causes[j] + '</dd>';
                            $('#lead dl').append(markup);
                        }
                    }
                }
                else {
                    var slug = this.slugify(record.cause);
                    var dt = $('#' + slug);
                    if ( dt.length ) {
                        dt.append(img);
                    }
                    else {
                        var markup = '<dt id="' + slug + '">' + img + '</dt><dd>' + record.cause + '</dd>';
                        $('#lead dl').append(markup);
                    }
                }
            }
        }
        else {
            $('#lead dl').html('');
        }
        $('#lead p').html('');
        $('#lead p').after('<p>Current service alert' + s + ' now for the ' + this.lines.subway.worsts.join(' and ') + '&nbsp;line' + s + end_of_graf + '</p>');
    },
    init: function() {
        // Loop through the data.
        // Figure out the last alert, also, add some helper attributes to the data.
        //
        // If a line has a value of -1 in its stop field, that means it's a current alert
        // and the timer should be zero and stay at zero.
        is_zero = 0;
        worst = { stop: '' };
        worsts = [];
        Array.prototype.forEach.call(this.d.current, function(item, i) {

            // Add the time since to each item
            //console.log(item, item['stop'], tracker.calc_time_since(item['stop']));
            tracker.d.current[i]['ago'] = tracker.calc_time_since(item['stop']);

            if ( item['stop'] === -1 ) {
                // If this is our first current alert, we reset the worsts array,
                // just in case there's some older alert already in it.
                if ( is_zero === 0 ) worsts = [item['line']];
                else worsts.push(item['line']);
                is_zero = 1;
            }

            // Log the current worst, in the case there are no active alerts.
            // We use this to populate the lead time when there are no active alerts.
            if ( is_zero == 0 ) {
                //console.log(item['stop'] > worst['stop'],item['stop'], worst['stop'])
                if ( item['stop'] > worst['stop'] ) {
                    worst = item;
                    worsts = [item['line']];
                }
                // In case we have multiple alerts that ended at the same time
                if ( item['stop'] == worst['stop'] && worsts.indexOf(item['line']) === -1 ) worsts.push(item['line']);
            }
            //console.log(i, item['line'], item['stop']);
        });
        // Sort the data
        this.sorted = this.d.current.sort(function(a, b) { return a.ago - b.ago });

        // Take the final worsts array and assign that to the object for later.
        this.lines.subway.worsts = worsts;
        if ( is_zero == 1 ) this.update_lead_alert();
        else this.update_lead_no_alert();

        this.update_recent();
    }
};


$.getJSON('data/current.json?' + tracker.rando(), function(data) {
    tracker.d.current = data;
    tracker.init();
});

var utils = {
    parse_time: function(time) {
        // time is a datetime-looking string such as "2017-07-25 11:32:00"
        // returns a Date object.
        console.log(typeof time, time);
        if ( typeof time !== 'string' ) return Date.now();
        var t = time.replace(' ', 'T');
        //console.log(time, Date.parse(t), t);
        return Date.parse(t);
    }
}

var charter = {
    d: {},
    p: {},
    log: {},
    dev: 0,
    config: {
        circle_radius: 10,
        utc_offset: -400,
        minutes_per_bin: 20,
    },
    id: 'day-chart',
    nyc_now: new Date(),
    minutes_since_midnight: null,
    hours_since_midnight: null,
    get_minutes_since_midnight: function(time) {
        // time is a datetime-looking string such as "2017-07-25 11:32:00" *it's also optional*
        // Gets the number of minutes from now to this morning's midnight,
        // unless an argument is given, in which case it delivers the number
        // of minutes between midnight and that time.
        // Note that it's not actual minutes, it's a five-minute bin of minutes.
        var now = new Date().getTime();
        var seconds_in_minute = 60, ms_in_sec = 1000, minutes_in_bin = 5;
        if ( time !== undefined ) now = utils.parse_time(time);
        var then = new Date( this.nyc_now.getFullYear(), this.nyc_now.getMonth(), this.nyc_now.getDate(), 0,0,0),
            diff = now - then.getTime();
        return Math.floor(diff/(ms_in_sec*seconds_in_minute*minutes_in_bin));
    },
    update: function() {
        // Adapted from https://bl.ocks.org/gcalmettes/95e3553da26ec90fd0a2890a678f3f69
        var t = d3.transition()
          .duration(2000);

        var data = this.d.archive;

        // Scale the range of the data
        console.log(data.length,this.y(data.length-1));
        this.y.domain([0, data.length]);

        // Set up the binning parameters for the histogram
        var nbins = this.minutes_since_midnight;
        //console.log("Minutes since midnight: ", nbins)
        var histogram = d3.histogram()
          .domain(this.x.domain())
          .thresholds(this.x.ticks(nbins))
          .value(function(d) { return d.value;} )

        // Compute the histogram
        var bins = histogram(data);

        radius = this.config.circle_radius;

        // bins objects
        var bin_container = this.svg.selectAll("g")
          .data(bins);

        bin_container.enter().append("g")
          .attr("transform", d => "translate("+this.x(d.x0)+", 0)");

        // JOIN new data with old elements.
        var dots = bin_container.selectAll("circle")
          .data(function(d) {
            return d.map(function(data, i){
                //if ( i == 0 ) console.log(data);
                return {"idx": i, "name": data.line, "value": data.value, "cause": data.cause, "start": data.start};}
                )
            });

        // EXIT old elements not present in new data.
        dots.exit()
            .attr("class", "exit")
          .transition(t)
            .attr("r", 0)
            .remove();

        // UPDATE old elements present in new data.
        dots.attr("class", "update");

        // ENTER new elements present in new data.
        dots.enter().append("circle")
          .attr("class", function(d) { return "subway" + d.name; })
          .attr("cx", 0) //g element already at correct x pos
          .attr("cy", function(d) {
                //console.log(charter.y(d.idx), charter.y(data.length-1)/2.2, radius,  charter.y(d.idx)-radius, charter.y(d.idx)-charter.y(data.length-1)/2.2);
              return charter.y(d.idx)-((radius*2)*d.idx)-radius; })
          .attr("r", 0)
          .merge(dots)
          .on("mouseover", function(d) {
              d3.select(this)
                .attr("class", "hover")
              charter.tooltip.transition()
                   .duration(200)
                   .style("opacity", .9);
              console.log(d);
              charter.tooltip.html(d.name + "<br/> (" + d.value + ")")
                .style("border", "3px solid red")
                .style("left", "200px")
                .style("top", "50px");
            })
            .on("mouseout", function(d) {
              d3.select(this)
                  .attr("class", "subway" + d.name);
                charter.tooltip.transition()
                     .duration(500)
                     .style("opacity", 0);
            })
          .transition()
            .duration(500)
            .attr("r", function(d) {
            return (d.length==0) ? 0 : radius; });
console.log(dots)

    },
    init: function() {
        this.minutes_since_midnight = this.get_minutes_since_midnight();
        this.hours_since_midnight = Math.floor(this.get_minutes_since_midnight()/(60/5));
        this.msms = [];
        var lower = 0;
        var bucket_size = Math.floor(this.config.minutes_per_bin/5);
        for ( var i = 0; lower <= this.minutes_since_midnight; i ++ ) {
            // Assign the upper and lower bound for each five-minute block
            lower = i * bucket_size;
            this.msms.push([lower, lower+(bucket_size-1)]);
        }
        // Build the data set we pass to the chart.
        // For this data set we need to know how many alerts existed within each five-minute window
        // from midnight until the current time.
        // That means we:
        // 1. Convert the record's start time to milliseconds, then to seconds, then to number of seconds since midnight, then divide it by five, rounding down.
        // 2. Do the same for the record's stop time, if the stop time is available.
        //  2a. If the stop time is not available we assign it the value of now.
        // 3. Loop through the number of five-minute bins since midnight
        // 4. In each loop, compare the bin against the delay's start and stop.
        //    If the bin is within the start and stop add it to the archive array.
        //    overlap = max(start1, start2) <= min(end1, end2)
        var bin_lens = {};  // For counting the most number of items we'll have in any bin
        for ( var i = 0; i < this.len; i ++ ) {
            this.d.archive_raw[i].start_bin = this.get_minutes_since_midnight(this.d.archive_raw[i].start);
            this.d.archive_raw[i].stop_bin = this.get_minutes_since_midnight(this.d.archive_raw[i].stop);
            var rec = this.d.archive_raw[i];

            // Loop through each minute-bin
            var len = this.msms.length;
            for ( var j = 0; j < len; j ++ ) {
                var overlap = Math.max(this.msms[j][0], rec.start_bin) <= Math.min(this.msms[j][1], rec.stop_bin);
                //var overlap = rec.start_bin <= j && j <= rec.stop_bin;
                //console.log(overlap, rec.start_bin, j, rec.stop_bin);
                if ( overlap ) {
                    rec.value = this.msms[j][0];
                    if ( typeof bin_lens[this.msms[j][0]] === 'undefined' ) bin_lens[this.msms[j][0]] = 1;
                    else bin_lens[this.msms[j][0]] += 1;
                    //rec.value = j;
                    this.d.archive.push(Object.assign({}, rec));
                }
            }
        }
        // Get the most number of items in any of the bins:
        this.log.max_count = Object.keys(bin_lens).reduce(function(a, b){ return bin_lens[a] > bin_lens[b] ? a : b });

        // Calculate the width (20 times the number of bins set in this.msms above),
        // set the dimensions of the graph
        var margin = {top: 10, right: 30, bottom: 30, left: 30},
            width = (len*20) - margin.left - margin.right,
            height = (bin_lens[this.log.max_count]*35) - 200 - margin.top - margin.bottom;
        console.log("HEIGHT", height, this.log.max_count, bin_lens)

        // Set the ranges
        this.x = d3.scaleLinear()
            .rangeRound([0, width])
            .domain([0, this.minutes_since_midnight]);

        this.y = d3.scaleLinear()
            .range([height, 0]);

        // Adds the svg canvas
        this.svg = d3.select("#" + this.id)
          .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          .append("g")
            .attr("transform",
                      "translate(" + margin.left + "," + margin.top + ")");

        // add the tooltip area to the webpage
        this.tooltip = d3.select('#' + this.id).append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        this.svg.append("g")
          .attr("class", "axis axis--x")
          .attr("transform", "translate(0," + height + ")")
          .call(d3.axisBottom(this.x).ticks(this.hours_since_midnight + 1));

        this.update();
        this.update();
    }
};
$.getJSON('data/archive.json?' + tracker.rando(), function(data) {
    charter.d.archive_raw = data;
    charter.d.archive = [];
    charter.len = data.length;
    charter.init();
});
