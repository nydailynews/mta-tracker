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
        console.log(time);
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
    parse_cause: function() {
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
 
