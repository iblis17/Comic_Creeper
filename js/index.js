var page = require('webpage').create();
var sys = require('system');
var url;

if (sys.args.length === 1) {
    console.log('Usage: index.js <url>');
    phantom.exit();
}

url = sys.args[1];

page.open(url, function() {
	page.includeJs("http://ajax.googleapis.com/ajax/libs/jquery/1.9.0/jquery.min.js", function() {
		var getindex = page.evaluate(function() {
			var tar = $("#rp_ctl00_tb_comic table table");
			var totle = "", i;

			$("#rp_ctl00_tb_comic script").remove();

			for(i=1; i<tar.size(); i++)
			{
				totle += tar.eq(i).text();
			}
			return totle;
		});
		console.log(getindex);
		phantom.exit()
	});
});
