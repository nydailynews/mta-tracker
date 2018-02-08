//**TODO add a countdown that lets a reader know how long until the next check for updates
console.info("USE console.info() TO LOG");
console.log = function() {}; 
var utils = {
    rando: function()
    {
        // Generate a random ascii string, useful for busting caches.
        var text = "";
        var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

        for( var i = 0; i < 20; i++ )
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
// Manages the lead graf, the list of recent alerts
var tracker = {
    d: {},
    config: {
        tz_offset: -5,
        utc_offset: -500,
        seconds_cutoff: 6 * 60 * 60,
        seconds_between_checks: 20,
    },
    now: Date.now(),
    calc_time_zone: function(offset) {
        // Get the current time in a different timezone. Must know the tz offset,
        // i.e. the number of hours ahead or behind GMT.
        var d = new Date();
        var utc = d.getTime() - (d.getTimezoneOffset() * 60000);
        return new Date(utc + (3600000 * offset));
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
        return Math.floor((Date.now() - t) / 1000);
    },
    convert_seconds: function(sec) {
        // Turns an integer into the representative number of minutes and hours.
        var hours = Math.floor(sec/3600);
        var minutes = Math.floor((sec-hours * 3600) / 60);
        var secs = sec % 60;
        //if ( minutes < 10 ) minutes = "0" + minutes;
        if ( secs < 10 ) secs = "0" + secs;
        if ( hours > 0 ) return hours + ':' + minutes + ':' + secs;
        return minutes + ':' + secs;
    },
    update_timer: function(id, value) {
        if ( document.getElementById(id) != null ) document.getElementById(id).innerHTML = value;
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
            //if ( shown > 6 && +item['ago'] > tracker.config.seconds_cutoff ) {
            if ( +item['ago'] > tracker.config.seconds_cutoff ) {
                class_attr = ' class="cutoff"';
                // This var helps us place the "More+" link
                if ( cutoff === 0 ) {
                    cutoff = shown;
                    $('#recent dl').append('<dt class="more"></dt><dd class="more"><a href="javascript:tracker.toggle_cutoff();">See all the lines</a></dd>');
                }
            }

            var markup = '<dt' + class_attr + '><img src="' + this.pathing + 'static/img/line_' + l + '.png" alt="Icon of the MTA ' + l + ' line"></dt>\n\
                <dd' + class_attr + '><time id="line-' + l + '">' + tracker.convert_seconds(item['ago']) + '</time> since the last alert</dd>';
            $('#recent dl').append(markup);
        });
        this.w = window.setInterval("tracker.count_up()", 1000);
    },
    toggle_cutoff: function() {
        $('.recent .cutoff').toggleClass('unhide');
        $('.recent .more').toggleClass('hide');
    },
    update_lead_no_alert: function() {
        // Write the lead and start the timer.
        // The worst time will be the first item in the sorted array
        this.update_timer('yes-no', 'NO');
        var latest = this.sorted[0];
        if ( latest['line'] === 'ALL' ) latest = this.sorted[1];
        if ( $('h2#yes-no + p').html('') == '' ) $('h2#yes-no + p').html('It’s been <time id="timer-text"></time> since the latest MTA subway service alert');
        this.update_timer('timer-text', this.convert_seconds(latest['ago']));
        // Update the p text
        var s = '', were = 'was';
        if ( this.lines.subway.worsts.length > 1 ) {
            s = 's';
            were = 'were';
        }
        //$('#lead p').text('since the last MTA subway service alert.');
        if ( $('h2#yes-no + p + p').length )  $('h2#yes-no + p + p').html('');
        $('h2#yes-no + p').after('<p>Latest service alert' + s + ' ' + were + ' for the ' + this.lines.subway.worsts.join(' and ') + '&nbsp;line' + s + '.</p>');
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
        var len = this.d.active.length;

        $('#lead dl').html('');

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
                var l = this.d.active[i];
                var cause = l.cause;
                if ( causes.indexOf(cause) === -1 ) {
                    // Add the cause to the list of causes
                    // so we know if the next cause is new or not.
                    causes.push(cause);
                    // Also associate the line with the cause so we can later
                    // put all/any lines with the same cause together.
                    groups[cause] = [l];
                }
                else {
                    // We have a duplicate cause
                    is_multiple = 1;
                    // We want to know which cause(s) are multiples.
                    multiples.push(cause);
                    groups[cause].push(l.line);
                }
            }

            // Next we generate and place the markup
            for ( var i = 0; i < len; i ++ ) {
                var l = this.d.active[i];
                var record = l;
                var img = '<img src="static/img/line_' + l.line + '.png" alt="MTA ' + l.line + ' line icon">';

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
        $('h2#yes-no + p').html('');
        var sentence = 'Current service alert' + s + ' now for the ' + this.lines.subway.worsts.join(' and ') + '&nbsp;line' + s + end_of_graf;
        if ( $('h2#yes-no + p + p').length )  $('h2#yes-no + p + p').html(sentence);
        else $('h2#yes-no + p').after('<p>Current service alert' + s + ' now for the ' + this.lines.subway.worsts.join(' and ') + '&nbsp;line' + s + end_of_graf + '</p>');
    },
	first_load: function() {
        // Loop through the data.
        // Figure out the last alert, also, add some helper attributes to the data.
        //
        // If a line has a value of -1 in its stop field, that means it's a current alert
        // and the timer should be zero and stay at zero.
        var is_zero = 0;
        var worst = { stop: '' };
        var worsts = [];
        Array.prototype.forEach.call(this.d.active, function(item, i) {
            console.info(item);
        });
        Array.prototype.forEach.call(this.d.current, function(item, i) {
            // Add the time since to each item
            //console.info(item, item['stop'], tracker.calc_time_since(item['stop']));
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
                //console.info(item['stop'] > worst['stop'],item['stop'], worst['stop'])
                if ( item['stop'] > worst['stop'] ) {
                    worst = item;
                    worsts = [item['line']];
                }
                // In case we have multiple alerts that ended at the same time
                if ( item['stop'] == worst['stop'] && worsts.indexOf(item['line']) === -1 ) worsts.push(item['line']);
            }
            //console.info(i, item['line'], item['stop']);
        });
        // Sort the data
        this.sorted = this.d.current.sort(function(a, b) { return a.ago - b.ago });

        // Take the final worsts array and assign that to the object for later.
        this.lines.subway.worsts = worsts;
        if ( this.d.active.length >= 1 ) this.update_lead_alert();
        else this.update_lead_no_alert();

        this.update_recent();
    },
    update_check: function() {
        // See if there's anything new to get.
        this.new_updates = 0;
		$.getJSON(tracker.pathing + 'data/active.json?' + utils.rando(), function(data) {
            console.info("ACTIVE-ALERTS DATA UPDATE CHECK:", tracker.d.active.length, data.length);
            if ( tracker.d.active.length !== data.length ) {
                console.info("");
                tracker.new_updates = Math.abs(tracker.d.active.length - data.length);
                tracker.d.active = data;
                $.getJSON(tracker.pathing + 'data/current.json?' + utils.rando(), function(data) {
                    // *** NEED TO PUBLISH WHAT HAS CHANGED
                    tracker.d.current = data;
                    tracker.first_load();
                });
                //charter.update_data();
                //charter.update();
            }
        });
        if ( this.new_updates > 0 ) {
            console.info(this.new_updates + " NEW UPDATES");
        }
    },
    init: function(pathing) {
		if ( pathing == null ) pathing = '';
		this.pathing = pathing;
		$.getJSON(pathing + 'data/active.json?' + utils.rando(), function(data) {
			tracker.d.active = data;
			//tracker.first_load();
            $.getJSON(pathing + 'data/current.json?' + utils.rando(), function(data) {
                tracker.d.current = data;
                tracker.first_load();
                // Set the timer to check for updated data
                tracker.interval = window.setInterval(tracker.update_check, tracker.config.seconds_between_checks * 1000);
            });
		});
	},

};

// CUOMO-CHART OBJECT
// Manages the Cuomo-oriented bar chart.
var cuomo = {
    d: {},
    p: {},
    next_check: 0,
    config: {
        in_dev: 0,
        hours_per_cuomo: 15,
        seconds_between_checks: 20,
		ceiling: 5,
		days_to_show: 7,
		dim: {
			'10': {
				image: 40,
				width: 460,
				height: 440
			},
			'7': {
				image: 57.14,
				width: 460,
				height: 327
			},
		}
    },
    id: 'weeks-chart',
    first_load: function() {
        var margin = {top: 10, right: 30, bottom: 30, left: 30},
            width = this.config.dim[this.config.days_to_show].width - margin.left - margin.right,
            height = this.config.dim[this.config.days_to_show].height - margin.top - margin.bottom;
        this.height = height;

        // Adds the svg canvas
        this.svg = d3.select("#" + this.id + ' svg')
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)

		var x = d3.scaleBand()
			.range([0, width], .1);
		var y = d3.scaleLinear()
			.range([height, 0]);

		var x_axis = d3.axisBottom(x);
		var y_axis = d3.axisLeft(y)
			.ticks(6);

		var chart = d3.select('#weeks-chart-svg')
			.attr("width", width + margin.left + margin.right)
			.attr("height", height + margin.top + margin.bottom)
			.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

		var data = [];
		for ( var property in this.d.archives ) {
			if ( this.d.archives.hasOwnProperty(property) ) {
				var seconds = this.d.archives[property].seconds;
				var minutes = Math.floor(seconds / 60);
				var hours = minutes / 60;
				var one_cuomo = Math.floor(hours / this.config.hours_per_cuomo);
				data.push({ 'date': property, 'delays': this.d.archives[property].delays, 'hours': hours, 'cuomos': one_cuomo});

			}
		}
		data.sort(function(a, b) { return +a['date'].replace(/-/g,'') > +b['date'].replace(/-/g,'')} );
		data = data.slice(this.config.days_to_show * -1);
		console.info(data);

		var ceiling = this.config.ceiling;
		x.domain(data.map(function(d) { return d['date'] }));
		y.domain([0, d3.max(data, function(d) { return ceiling; })]);

		chart.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height + ")")
			.call(x_axis)
			.append("text")
			.attr("x", 10)
			.attr("dy", "2.5em")
			.style("text-anchor", "start")
			.text('Day');

        /*
		chart.append("g")
			.attr("class", "y axis")
			.call(y_axis)
			.append("text")
			.attr("transform", "rotate(-90)")
			.attr("y", 6)
			.attr("dy", ".71em")
			.style("text-anchor", "end")
			.text('Cuomos');
            */

		chart.selectAll("bar")
			.data(data)
			.enter().append("rect")
			.attr("class", "bar cuomos")
			.attr("fill", "url(#barbg)")
			.attr("x", function(d) { return x(d['date']); })
			.attr("width", x.bandwidth())
			.attr("y", function(d) { return y(d['cuomos']); })
			.attr("height", function(d) { return height - y(d['cuomos']); });
    },
    init: function(pathing) {
		if ( pathing == null ) pathing = '';
		this.pathing = pathing;
		$('#barbg').attr('width', this.config.dim[this.config.days_to_show].image);
		$('#barbg').attr('height', this.config.dim[this.config.days_to_show].image);
		$('#barbg image').attr('width', this.config.dim[this.config.days_to_show].image);
		$('#barbg image').attr('height', this.config.dim[this.config.days_to_show].image);
		$.getJSON(pathing + 'data/archives-10.json?' + utils.rando(), function(data) {
			cuomo.d.archives = data;
			//cuomo.first_load();
            // Set the timer to check for updated data
            cuomo.first_load();
            $.getJSON(pathing + 'data/archives-average-30.json?' + utils.rando(), function(data) {
                // Flesh out the on-average sentence.
                document.getElementById('hours-average').textContent = Math.round( data.average.weekday * 10 ) / 10;
                var cuomos = Math.round( (data.average.weekday/cuomo.config.hours_per_cuomo) * 10 ) / 10;
                var cuomos_whole = Math.floor(cuomos);
                var cuomos_img = '';
                for ( var i = 0; i < cuomos_whole; i ++ ) cuomos_img += '<img src="img/cuomo-circle-large.png" alt="one Cuomo" class="cuomo">';
                document.getElementById('hours-cuomos').innerHTML = cuomos_img;
            });
		});
	}
};
cuomo.init();


// CHARTER OBJECT
// Manages the chart of today's alerts in the middle of the page.
var charter = {
    d: {},
    p: {},
    log: {},
    next_check: 0,
    config: {
        in_dev: 0,
        utc_offset: -500,
        circle_radius: 10,
        minutes_per_bin: 30,
        seconds_between_checks: 20,
        height_factor: 29, //
    },
    rundown: {
        alerts: 0,
        lines: [],
        seconds: 0,
    },
    id: 'day-chart',
    update_rundown: function() {
        // Write the rundown graf.
        var r = this.rundown;
        graf = 'Today there have been ' + r.alerts + ' service alerts on ' + r.lines_len + ' different lines \n\
            totalling ' + r.hours + ' hours and ' + r.minutes + ' minutes of alert-time.';
		if ( document.getElementById('rundown') !== null ) document.getElementById('rundown').innerHTML = graf;
    },
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

        // bins objects:
        // each "g" svg element is a column, and in that column are somewhere between zero
        // and X number of "circle" svg elements.
        var bin_container = this.svg.selectAll("g")
          .data(bins);

        bin_container.enter().append("g")
          .attr("transform", d => "translate("+this.x(d.x0)+", 0)");

        // JOIN new data with old elements.
        var dots = bin_container.selectAll("circle")
          .data(function(d) {
            return d.map(function(data, i) {
                //if ( i == 0 ) console.info('DATA', data);
                return {
                    "idx": i,
                    "minutes": data.minutes,
                    "order": data.order,
                    "name": data.line,
                    "value": data.time,
                    "cause": data.cause,
                    "start": data.start,
                    "stop": data.stop,
                    };
                }
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
          .attr("id", function(d) { return d.idx + "-subway" + d.name + "-cause-" + utils.slugify(d.cause); })
          .attr("class", function(d) { return "subway" + d.name + " cause" + utils.slugify(d.cause); })
          .attr("cx", 0) // g element already at correct x pos
          .attr("cy", function(d) {
              // TODO: Write what's actually happening here.
                // return d.idx * (radius*2);   // <-- In case we want the circles on the ceiling
                //
                // That "10" below id the bottom margin
                return charter.height - (d.idx * (radius*2)) - 10;
          })
          .attr("r", 0)
          .merge(dots)
          .on("mouseover", function(d) { charter.on_circle_mouseover(d) } )
          .on("mouseout", function(d) {
                charter.on_circle_mouseout(d);
                d3.select(this)
                  .attr("class", "subway" + d.name + " cause" + utils.slugify(d.cause));
            })
          .transition()
            .duration(500)
            .attr("r", function(d) {
                return (d.length==0) ? 0 : radius; });

    },
    on_circle_mouseover: function(d) {
        // Helper function for the part in update() where we add the circles to the chart
        // and assign mouseover functionality
        d3.select(this)
        charter.tooltip.transition()
           .duration(200)
           .style("opacity", .9);
        console.info(d);
        charter.tooltip.html("<span class='line-" + d.name + "'>" + d.name + "</span> line alert\n\
            from " + utils.human_time(d.start) + " until " + utils.human_time(d.stop) + ",\n\
            <br>Cause: " + d.cause);
        $('circle').attr('opacity', '.2');
        $('.cause' + utils.slugify(d.cause)).css({ 'fill': '', 'stroke-width': '5' });
        $('.cause' + utils.slugify(d.cause)).attr('opacity', '1');
    },
    on_circle_mouseout: function(d) {
        // Helper function for the part in update() where we add the circles to the chart
        // and assign mouseout functionality
        charter.tooltip.transition()
             .duration(500)
             .style("opacity", 0);
        $('circle').attr('opacity', '1');
        $('.cause' + utils.slugify(d.cause)).css({ 'fill': '', 'stroke-width': '1' });
    },
    update_check: function() {
        // See if there's anything new to get.
        $.getJSON('data/archive.json?' + utils.rando(), function(data) {
            var prev_len = charter.len;
            console.info("CHART DATA UPDATE CHECK:", prev_len, data.length);
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
            this.d.archive_raw[i].minutes = this.d.archive_raw[i].stop_bin - this.d.archive_raw[i].start_bin;
            //console.info(this.d.archive_raw[i].start, this.d.archive_raw[i].start_bin, this.d.archive_raw[i].stop, this.d.archive_raw[i].stop_bin);
            var rec = this.d.archive_raw[i];

            // Add the line and second-length of delay to the rundown
            if ( this.rundown.lines.indexOf(rec['line']) === -1 ) this.rundown.lines.push(rec['line']);
            this.rundown.seconds += rec['length'];

            // Step 4. Loop through each minute-bin
            var len = this.msms.length;
            for ( var j = 0; j < len; j ++ ) {
                var overlap = Math.max(this.msms[j][0], rec.start_bin) <= Math.min(this.msms[j][1], rec.stop_bin);
                //var overlap = rec.start_bin <= j && j <= rec.stop_bin;
                //console.info(overlap, rec.start_bin, j, rec.stop_bin);
                if ( overlap ) {
                    rec.minutes_since_bin = this.msms[j][0];
                    rec.value = this.msms[j][0];
                    rec.time = new Date();
                    rec.time.setTime(this.midnight + this.msms[j][0] * 60 * 1000 ); // Convert the X-minute bin number to milliseconds.
                    rec.minutes = this.d.archive_raw[i].minutes;
                    rec.order = i;
                    //console.info(rec)
                    if ( typeof this.bin_lens[this.msms[j][0]] === 'undefined' ) this.bin_lens[this.msms[j][0]] = 0;
                    this.bin_lens[this.msms[j][0]] += 1;
                    this.d.archive.push(Object.assign({}, rec));
                }
            }
        }
        //this.d.archive.sort(function(a, b) { if ( a.minutes > b.minutes ) return 0; return 1; } );
        //this.d.archive.sort(function(a, b) { if ( a.order > b.order ) return 0; return 1; } );

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
        //console.info("ASDAS", this.bin_lens[this.log.max_count]);

        var max_count = this.bin_lens[this.log.max_count];
        // DEV-SPECIFIC
        if ( document.location.hash !== '' ) {
           var hash = document.location.hash.substring(1);
           if ( +hash > 0 ) max_count = +document.location.hash.substring(1);
        }

        if ( max_count <= 10 ) {
            this.config.height_factor += 5;
        }
        if ( max_count >= 20 ) {
            this.config.height_factor -= 10;
        }
        var margin = {top: 10, right: 30, bottom: 30, left: 30},
            width = (this.msms.length*(this.config.circle_radius*2) + 2) - margin.left - margin.right,
            height = (max_count*this.config.height_factor) - 0 - margin.top - margin.bottom;
        this.height = height;
        console.info("HEIGHT", height, "MAX COUNT", this.bin_lens[this.log.max_count], "BIN_LENS", this.bin_lens)
        if ( height < 120 ) height = 120;
        if ( height > 800 ) height = 800;

        // Set the ranges
        this.x = d3.scaleTime()
            .domain([this.midnight, new Date().setHours(this.hours_since_midnight + 1, 0, 0, 0)])
            .range([0, Math.floor(this.minutes_since_midnight/this.config.minutes_per_bin)*(this.config.circle_radius*2)])

        this.y = d3.scaleLinear()
            .range([height, 0]);

        // Adds the svg canvas
        this.svg = d3.select("#" + this.id + ' svg')
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
	// The work we need to do to load the chart.
    first_load: function() {
        this.tooltip = d3.select('#tooltip')

        this.update_data();
        this.draw_chart();
        this.update();
        this.update();

        // When scrolled into view, trigger the mouseover for the latest alert.
        var nodes = charter.svg.selectAll('g').selectAll('circle').nodes();
        var len = nodes.length;
        n = nodes[len - 1];
		var waypoint = new Waypoint({
		  element: document.getElementById('day-chart-svg'),
		  handler: function(direction) {
			$.fn.triggerSVGEvent = function(eventName) {
				 var event = document.createEvent('SVGEvents');
				 event.initEvent(eventName,true,true);
				 this[0].dispatchEvent(event);
				 return $(this);
			};
			$('#' + n.id).triggerSVGEvent('mouseover');
		  },
		  offset: window.innerHeight - 200
		})

        // Set the timer to check for updated data
        this.interval = window.setInterval(this.update_check, this.config.seconds_between_checks * 1000);

        // Scroll the chart (it scrolls on handheld) all the way to the right on handheld.
        if ( is_mobile ) document.getElementById('chart-wrapper').scrollLeft = 10000;

		// Build a list of distinct alerts for the cause-list
        for ( var i = 0; i < this.len; i ++ ) {
			var cause = this.d.archive_raw[i].cause;
			if ( this.causes.indexOf(cause) === -1 ) {
				this.causes.push(cause);
				$('#alerts ol').append('<li class="cause' + utils.slugify(cause) + '">' + cause + '</li>');
			}
		}
		$('#alerts-number').text(this.causes.length);
    },
	causes: [],
    init: function(pathing) {
		if ( pathing == null ) pathing = '';
		this.pathing = pathing;
		$.getJSON(pathing + 'data/archive.json?' + utils.rando(), function(data) {
			charter.d.archive_raw = data;
			charter.d.archive = [];
			charter.len = data.length;
			charter.first_load();
		});
	},
};

// Every 15 minutes
var parpar = window.setInterval(function() { if ( typeof PARSELY !== 'undefined' ) PARSELY.beacon.trackPageView({ url: document.location.href, urlref: document.location.href, js: 1 }) }, 900000);
