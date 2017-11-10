//**TODO add a countdown that lets a reader know how long until the next check for updates
var utils = {
    rando: function()
    {
        // Generate a random ascii string, useful for busting caches.
        var text = "";
        var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

        for( var i=0; i < 20; i++ )
            text += possible.charAt(Math.floor(Math.random() * possible.length));

        return text;
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
    add_zero: function(i) {
        // For values less than 10, return a zero-prefixed version of that value.
        if ( i < 10 ) return "0" + i;
        return i;
    },
    parse_time: function(time) {
        // time is a datetime-looking string such as "2017-07-25 11:32:00"
        // returns a unixtime integer.
        if ( typeof time !== 'string' ) return Date.now();

        var time_bits = time.split(' ')[1].split(':');
        var date_bits = time.split(' ')[0].split('-');
        // We do that "+date_bits[1] - 1" because months are zero-indexed.
        var d = new Date(date_bits[0], +date_bits[1] - 1, date_bits[2], time_bits[0], time_bits[1], time_bits[2]);
        return d.getTime();
    },
    human_time: function(time) {
        // time is a datetime-looking string such as "2017-07-25 11:32:00"
        // returns a human-readable string, "11:32 a.m."
        if ( time === null ) return 'now';

        var time_bits  = time.split(' ')[1].split(':');
        var ampm = 'a.m.';
        // Remove the seconds
        time_bits.pop();
        if ( +time_bits[0] > 11 )
        {
            ampm = 'p.m.'
            time_bits[0] = +time_bits[0] - 12;
            if ( time_bits[0] === 0 ) time_bits[0] = 12;
        }
        return time_bits.join(':') + ' ' + ampm;
    },
}

// TRACKER OBJECT
// Manages the lead graf, the list of recent alerts at the bottom
var tracker = {
    d: {},
    config: {
        tz_offset: -5,
        utc_offset: -500,
        seconds_cutoff: 6 * 60 * 60,
    },
    now: Date.now(),
    calc_time_zone: function(offset) {
        // Get the current time in a different timezone. Must know the tz offset,
        // i.e. the number of hours ahead or behind GMT.
        var d = new Date();
        var utc = d.getTime() - (d.getTimezoneOffset() * 60000);
        return new Date(utc + (3600000*offset));
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
            if ( hours > 0 ) time = hours + ':' + utils.add_zero(mins) + ':' + utils.add_zero(secs);
            else time = mins + ':' + utils.add_zero(secs);
            $(this).text(time);
        });
    },
    calc_time_since: function(time) {
        // time is a datetime-looking string such as "2017-07-25 11:32:00"
        if ( time <= 0 ) return 0;
        var t = utils.parse_time(time);
        return Math.floor((Date.now() - t)/1000);
    },
    convert_seconds: function(sec) {
        // Turns an integer into the representative number of minutes and hours.
        var hours = Math.floor(sec/3600);
        var minutes = Math.floor((sec-hours*3600)/60);
        var secs = sec%60;
        //if ( minutes < 10 ) minutes = "0" + minutes;
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
        cutoff = 0;
        Array.prototype.forEach.call(this.sorted, function(item, i) {
            var l = item['line'];
            if ( l == 'ALL' ) return false;
            if ( tracker.lines.subway.worsts.indexOf(l) > -1 ) return false;
            shown += 1;
            if ( item['ago'] > 100332086 ) return false;

            // We define the cutoff for display in the config.
            // If the seconds are greater than the config we add a class to the item.
            var class_attr = '';
            if ( shown > 6 && +item['ago'] > tracker.config.seconds_cutoff ) {
                class_attr = ' class="cutoff"';
                // This var helps us place the "More+" link
                if ( cutoff === 0 ) {
                    cutoff = shown;
                    $('#recent dl').append('<dt class="more"></dt><dd class="more"><a href="javascript:tracker.toggle_cutoff();">More</a></dd>');
                }
            }

            var markup = '<dt' + class_attr + '><img src="static/img/line_' + l + '.png" alt="Icon of the MTA ' + l + ' line"></dt>\n\
                <dd' + class_attr + '><time id="line-' + l + '">' + tracker.convert_seconds(item['ago']) + '</time> since the last alert</dd>';
            $('#recent dl').append(markup);
        });
        w = window.setInterval("tracker.count_up()", 1000);
    },
    toggle_cutoff: function() {
            $('.recent .cutoff').toggleClass('unhide');
            $('.recent .more').toggleClass('hide');
    },
    update_lead_no_alert: function() {
        // Write the lead and start the timer.
        // The worst time will be the first item in the sorted array
        //$('#lead h1').text('MTA Tracker');
        this.update_timer('yes-no', 'NO');
        var latest = this.sorted[0];
        if ( latest['line'] === 'ALL' ) latest = this.sorted[1];
        this.update_timer('timer-text', this.convert_seconds(latest['ago']));
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
                        var slug = utils.slugify(causes[j]);
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
                    var slug = utils.slugify(record.cause);
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
        var is_zero = 0;
        var worst = { stop: '' };
        var worsts = [];
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

$.getJSON('data/current.json?' + utils.rando(), function(data) {
    tracker.d.current = data;
    tracker.init();
});

// CHARTER OBJECT
// Manages the chart of today's alerts in the middle of the page.
var charter = {
    d: {},
    p: {},
    log: {},
    in_dev: 0,
    next_check: 0,
    config: {
        utc_offset: -500,
        circle_radius: 10,
        minutes_per_bin: 20,
        seconds_between_checks: 20,
        radius_factor: 1.9,
        height_factor: 30,
    },
    rundown: {
        alerts: 0,
        lines: [],
        seconds: 0,
    },
    update_rundown: function() {
        // Write the rundown graf.
        var r = this.rundown;
        graf = 'Today there have been ' + r.alerts + ' service alerts on ' + r.lines_len + ' different lines \n\
            totalling ' + r.hours + ' hours and ' + r.minutes + ' minutes of alert-time.';
        document.getElementById('rundown').innerHTML = graf;
    },
    id: 'day-chart',
    midnight: new Date().setHours(0, 0, 0, 0),
    nyc_now: new Date(),
    minutes_since_midnight: null,
    hours_since_midnight: null,
    get_minutes_since_midnight: function(time) {
        // time is a datetime-looking string such as "2017-07-25 11:32:00" *it's also optional*
        // Gets the number of minutes from now to this morning's midnight,
        // unless an argument is given, in which case it delivers the number
        // of minutes between midnight and that time.
        // Note that it's not actual minutes, it's a five-minute bin of minutes.
        var seconds_in_minute = 60, ms_in_sec = 1000;
        var now = new Date().getTime();
        if ( time !== undefined ) now = utils.parse_time(time);

        var diff = now - this.midnight,
            minutes = Math.floor(diff/(ms_in_sec*seconds_in_minute));
        return minutes;
    },
    update: function() {
        // Adapted from https://bl.ocks.org/gcalmettes/95e3553da26ec90fd0a2890a678f3f69
        var t = d3.transition()
          .duration(2000);

        var data = this.d.archive;

        // Scale the range of the data
        this.y.domain([0, data.length]);

        // Set up the binning parameters for the histogram
        var nbins = this.minutes_since_midnight;
        
        var histogram = d3.histogram()
          .domain(this.x.domain())
          .thresholds(this.x.ticks(nbins))
          .value(function(d) { return d.time; } )

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
                //if ( i == 0 ) console.log('DATA', data);
                return {"idx": i, "name": data.line, "value": data.time, "cause": data.cause, "start": data.start, "stop": data.stop};}
                )
            });

        // EXIT old elements not present in new data.
        dots.exit()
            .attr("class", "exit")
          .transition(t)
            .attr("r", 0)
            .remove();

        // UPDATE old elements present in new data.
        dots.attr("class", function(d) { return "update subway" + d.name; });

        // ENTER new elements present in new data.
        dots.enter().append("circle")
          .attr("class", function(d) { return "subway" + d.name; })
          .attr("cx", 0) //g element already at correct x pos
          .attr("cy", function(d) {
                return charter.y(d.idx)-((radius*charter.config.radius_factor)*d.idx)-(radius); })
          .attr("r", 0)
          .merge(dots)
          .on("mouseover", function(d) {
              d3.select(this)
              charter.tooltip.transition()
                   .duration(200)
                   .style("opacity", .9);
              console.log(d);
              charter.tooltip.html("<span class='line-" + d.name + "'>" + d.name + "</span> line alert\n\
                    from " + utils.human_time(d.start) + " until " + utils.human_time(d.stop) + ",\n\
                    <br>Cause: " + d.cause);
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

    },
    update_check: function() {
        // See if there's anything new to get.
        $.getJSON('data/archive.json?' + utils.rando(), function(data) {
            var prev_len = charter.len;
            console.log("DATA UPDATE CHECK:", prev_len, data.length);
            if ( prev_len !== data.length ) {
                charter.d.archive_raw = data;
                charter.d.archive = [];
                charter.len = data.length;
                charter.update_data();
                charter.update();
            }
        });
    },
    update_data: function() {
        // Assuming the d.archive data is current, update the data the chart uses to publish.
        this.minutes_since_midnight = this.get_minutes_since_midnight();
        this.hours_since_midnight = Math.floor(this.minutes_since_midnight/60);
        this.msms = [];
        var lower = 0;
        var bucket_size = Math.floor(this.config.minutes_per_bin);
        // Assign the upper and lower bound for each X-minute block
        var ceiling = Math.floor(this.minutes_since_midnight/1);
        for ( var i = 0; lower <= ceiling; i ++ ) {
            lower = i * bucket_size;
            this.msms.push([lower, lower+(bucket_size-1)]);
        }
        // Build the dataset we pass to the chart.
        // For this dataset we need to know how many alerts existed within each
        // X-minute window from midnight until the current time.
        // That means we:
        // 1. Loop through each record.
        // 2. Convert each record's start time to milliseconds, then to seconds,
        //    then to minutes, then to number of minutes since midnight.
        // 3. Do the same for the record's stop time, if the stop time is available.
        //    3a. If the stop time is not available we assign it the value of now.
        // 4. Loop through the number of X-minute bins.
        // 5. In the loop, compare the bin against the delay's start and stop.
        //    If the bin is within the start and stop add a copy of the record to the archive array.
        //    overlap = max(start1, start2) <= min(end1, end2)
        this.bin_lens = {};  // For counting the most number of items we'll have in any bin
        // Step 1. Loop through each record.
        for ( var i = 0; i < this.len; i ++ ) {
            // Steps 2 and 3.
            this.d.archive_raw[i].start_bin = this.get_minutes_since_midnight(this.d.archive_raw[i].start);
            this.d.archive_raw[i].stop_bin = this.get_minutes_since_midnight(this.d.archive_raw[i].stop);
            //console.log(this.d.archive_raw[i].start, this.d.archive_raw[i].start_bin, this.d.archive_raw[i].stop, this.d.archive_raw[i].stop_bin);
            var rec = this.d.archive_raw[i];

            // Add the line and second-length of delay to the rundown
            if ( this.rundown.lines.indexOf(rec['line']) === -1 ) this.rundown.lines.push(rec['line']);
            this.rundown.seconds += rec['length'];

            // Step 4. Loop through each minute-bin
            var len = this.msms.length;
            for ( var j = 0; j < len; j ++ ) {
                var overlap = Math.max(this.msms[j][0], rec.start_bin) <= Math.min(this.msms[j][1], rec.stop_bin);
                //var overlap = rec.start_bin <= j && j <= rec.stop_bin;
                //console.log(overlap, rec.start_bin, j, rec.stop_bin);
                if ( overlap ) {
                    rec.minutes_since_bin = this.msms[j][0];
                    rec.value = this.msms[j][0];
                    rec.time = new Date();
                    rec.time.setTime(this.midnight + this.msms[j][0] * 60 * 1000 ); // Convert the X-minute bin number to milliseconds.
                    //console.log(rec)
                    if ( typeof this.bin_lens[this.msms[j][0]] === 'undefined' ) this.bin_lens[this.msms[j][0]] = 0;
                    this.bin_lens[this.msms[j][0]] += 1;
                    this.d.archive.push(Object.assign({}, rec));
                }
            }
        }
        // Get the most number of items in any of the bins:
        this.log.max_count = Object.keys(this.bin_lens).reduce(function(a, b){ return charter.bin_lens[a] > charter.bin_lens[b] ? a : b });

        // Populate the numbers we use in the day's rundown.
        this.rundown.alerts = this.d.archive_raw.length;
        this.rundown.lines_len = this.rundown.lines.length;
        this.rundown.hours = Math.floor(this.rundown.seconds / 3600);
        this.rundown.minutes = Math.floor(this.rundown.seconds / 60) % 60;
        this.update_rundown();
    },
    draw_chart: function() {
        // Calculate the width (20 times the number of bins set in this.msms above),
        // set the dimensions of the graph
        var len = this.msms.length;
        //console.log("ASDAS", this.bin_lens[this.log.max_count]);

        var max_count = this.bin_lens[this.log.max_count];
        // DEV-SPECIFIC
        if ( document.location.hash !== '' ) max_count = +document.location.hash.substring(1);

        if ( max_count <= 10 ) {
            this.config.height_factor += 6;
            this.config.radius_factor -= .4;
        }
        else if ( max_count >= 20 ) {
            this.config.height_factor -= 3;
            this.config.radius_factor -= .4;
        }

        var margin = {top: 10, right: 30, bottom: 30, left: 30},
            width = (len*20) - margin.left - margin.right,
            height = (max_count*this.config.height_factor) - 46 - margin.top - margin.bottom;
        console.log("HEIGHT", height, "MAX COUNT", this.bin_lens[this.log.max_count], "BIN_LENS", this.bin_lens)
        if ( height < 120 ) height = 120;
        if ( height > 800 ) height = 800;

        // Set the ranges
        this.x = d3.scaleTime()
            .domain([this.midnight, new Date().setHours(this.hours_since_midnight + 1, 0, 0, 0)])
            .range([0, this.minutes_since_midnight])

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

        this.svg.append("g")
          .attr("class", "axis axis--x")
          .attr("transform", "translate(0," + height + ")")
          .call(d3.axisBottom(this.x)
                .ticks(this.hours_since_midnight + 1)
                .tickFormat(d3.timeFormat("%-I %p"))
            );
    },
    init: function() {
        // The work we need to do to load the chart.
        this.tooltip = d3.select('#tooltip')

        this.update_data();
        this.draw_chart();
        this.update();
        this.update();

        // Set the timer to check for updated data
        //this.interval = window.setInterval(this.update_check, this.config.seconds_between_checks * 1000);

        // Scroll the chart (it scrolls on handheld) all the way to the right on handheld.
        if ( is_mobile ) document.getElementById('chart-wrapper').scrollLeft = 10000;
    }
};
$.getJSON('data/archive.json?' + utils.rando(), function(data) {
    charter.d.archive_raw = data;
    charter.d.archive = [];
    charter.len = data.length;
    charter.init();
});
