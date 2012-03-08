chatter = {
	startfrom: 0,
	poll: function() {
		$.getJSON('/poll', {startfrom:chatter.startfrom}, function(json){
			if (json.data.length) {
                chatter.startfrom = json.startfrom;
                for (i in json.data) {
                    chatter.startfrom += 1;

                    text = json.data[i].text;
                    screen_name = json.data[i].screen_name;
                    created_at = json.data[i].created_at;

                    tweetstr  = '<div class="screen_name">'+screen_name+' said:</div>';
                    tweetstr += '<div>'+text+'</div>';
                    tweetstr += '<div class="date">'+created_at+'</div>';
                    tweet = $('<div class="tweet"></div>').html(tweetstr).hide();
                    $('#chatter').prepend(tweet);
                    tweet.slideDown();
                }
            }

            setTimeout(chatter.poll, 1000);
		});
	},

}

$(document).ready(function() {
	$("#reload").click(function(){
		data = {terms:$('#terms').val()};
		$.post('/setterms', data, function(json){
			console.log('clb',json);
		}, 'json')

	});

    $(".btn").click(function(){
        data = {terms:$(this).html()};
        $.post('/setterms', data, function(json){
            console.log('clb',json);
        }, 'json')
    });
    $('.btn-group').children(':first-child').button('toggle');

	setTimeout(chatter.poll, 1000);
});