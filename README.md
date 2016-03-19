
Reddit-songs-to-youtube-bot
======
A Bot that replies with the Youtube link of a song that was mentioned in the comments.

The bot will go through every comment and will search if the comment is a song in a website that has a massive collection of song lyrics. If the mentioned song is in the website database the bot will search the song name on youtube and will retrieve the first result (I didn't think of a better way as of yet). After retrieving the youtube link the bot will reply to the comment with the youtube link.

======

The bot will auto-clean its database every 10 cycles. It will keep the latest (2 * MAXPOSTS) items, so disk space isn't wasted by comments you'll never see again anyway.
Python dependencies
======

1. [**Praw**](https://praw.readthedocs.org/en/stable/)
2. [**BeautifulSoup**](http://www.crummy.com/software/BeautifulSoup/bs4/doc/)
3. [**lxml**](http://lxml.de/)
