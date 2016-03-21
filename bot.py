#!/usr/bin/env python
# -*- coding: utf-8 -*-

#a bot that replies with youtube songs that were mentioned in the comments
import re
import socket
import sqlite3
import sys
import time
import traceback
import urllib
import urllib2

import praw
from bs4 import BeautifulSoup

'''USER CONFIGURATION'''

APP_ID = ""
APP_SECRET = ""
APP_URI = ""
APP_REFRESH = ""
    # https://www.reddit.com/comments/3cm1p8/how_to_make_your_bot_use_oauth2/
USERAGENT = "Python automatic youtube linkerbot"
# This is a short description of what the bot does.
# For example "Python automatic replybot v2.0 (by /u/GoldenSights)"
SUBREDDIT = "90sHipHop+altrap+asianrap+backspin+ChapHop+Gfunk+HipHopHeads+Rap+rapverses+trapmuzik+Turntablists+80sHardcorePunk+90sAlternative+90sRock+AlternativeRock+AltCountry+AORMelodic+ausmetal+BlackMetal+bluegrass+Blues+bluesrock+CanadianClassicRock+CanadianMusic+ClassicRock+country+Christcore+crunkcore+deathcore+deathmetal+Djent+DoomMetal+Emo+EmoScreamo+folk+folkmetal+folkpunk+folkrock+GaragePunk+GothicMetal+Grunge+hardcore+HardRock+horrorpunk+indie_rock+jrock+krautrock+MathRock+melodicdeathmetal+MelodicMetal+MetalNews+metal+metalcore+monsterfuzz+neopsychedelia+NewWave+noiserock+numetal+pianorock+poppunkers+PostHardcore+PostRock+powermetal+powerpop+ProgMetal+progrockmusic+PsychedelicRock+punk+Punkskahardcore+Punk_Rock+Rock+shoegaze+stonerrock+symphonicblackmetal+symphonicmetal+synthrock+truethrash+Truemetal+OutlawCountry+WomenRock+90sHipHop+altrap+asianrap+backspin+ChapHop+Gfunk+HipHopHeads+Rap+rapverses+trapmuzik+Turntablists+scottishmusic+danktunes+albumaday+albumoftheday+Albums+albumlisteners+bassheavy+Catchysongs+CircleMusic+CoverSongs+DutchMusic+EarlyMusic+earlymusicalnotation+FemaleVocalists+findaband+freemusic+jazz+Frisson+gameofbands+GayMusic+germusic+HeadNodders+heady+HeyThatWasIn+HighFidelity+ifyoulikeblank+indie+Instrumentals+IndieWok+ipm+IsolatedVocals+japanesemusic+LetsTalkMusic+listentoconcerts+listentomusic+ListenToThis+ListenToUs+livemusic+Lyrics+mainstreammusic+MiddleEasternMusic+Music+MusicAlbums+musicsuggestions+MusicToSleepTo+musicvideos+NewAlbums+newmusic+onealbumaweek+partymusic+RedditOriginals+RepublicOfMusic+RoyaltyFreeMusic+SlavicMusicVideos+SpotifyMusic+ThemVoices+unheardof+WhatIListenTo+WTFMusicVideos+music+tipofmytongue+namethattune+whatsthatsong+whatsthesong+whatsthissong+NameThatSong+kqly+311+ADTR+AliciaKeys+ArcadeFire+ArethaFranklin+APerfectCircle+TheAvettBrothers+BaysideIsACult+TheBeachBoys+Beatles+billytalent+Blink182+BMSR+BoBurnham+boniver+brandnew+BruceSpringsteen+Burial+ChristinaAguilera+cityandcolour+Coldplay+CutCopy+TheCure+DaftPunk+DavidBowie+Deadmau5+DeathCabforCutie+DeathGrips+DeepPurple+Deftones+DieAntwoord+DMB+elliegoulding+Eminem+empireofthesun+EnterShikari+Evanescence+feedme+FirstAidKit+flaminglips+franzferdinand+Gorillaz+gratefuldead+Greenday+GunsNRoses+Incubus+JackJohnson+JackWhite+JanetJackson+John_frusciante+kings_of_leon+Korn+ladygaga+lanadelrey+lennykravitz+Led_Zeppelin+lorde+Macklemore+Madonna+Manowar+MariahCarey+MattAndKim+Megadeth+Metallica+MGMT+MichaelJackson+MinusTheBear+ModestMouse+Morrissey+mrbungle+MyChemicalRomance+Muse+NeilYoung+NIN+Nirvana+NOFX+oasis+Opeth+OFWGKTA+OutKast+panicatthedisco+PearlJam+phish+Pinback+PinkFloyd+porcupinetree+prettylights+Puscifer+Queen+Radiohead+RATM+RedHotChiliPeppers+The_Residents+RiseAgainst+Rush+SigurRos+Slayer+slipknot+SmashingPumpkins+SparksFTW+TeganAndSara+TheKillers+TheOffspring+TheStrokes+TheMagneticZeros+tragicallyhip+ToolBand+U2Band+Umphreys+UnicornsMusic+velvetunderground+Ween+weezer+WeirdAl+yesband+Zappa"
# This is the sub or list of subs to scan for new posts. For a single sub, use "sub1". For multiple subreddits, use "sub1+sub2+sub3+..."
DO_SUBMISSIONS = False
DO_COMMENTS = True
# Look for submissions, comments, or both.
KEYWORDS = [""]
# These are the words you are looking for
KEYAUTHORS = []
# These are the names of the authors you are looking for
# The bot will only reply to authors on this list
# Keep it empty to allow anybody.
#REPLYSTRING = "**Hi, I'm a bot.**"
# This is the word you want to put in reply
MAXPOSTS = 100
# This is how many posts you want to retrieve all at once. PRAW can download 100 at a time.
WAIT = 30
# This is how many seconds you will wait between cycles. The bot is completely inactive during this time.
STOPWORDS=[" By "," by ","-"]
CLEANCYCLES = 10
# After this many cycles, the bot will clean its database
# Keeping only the latest (2*MAXPOSTS) items

'''All done!'''


print('Opening SQL Database')
sql = sqlite3.connect('sql.db')
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(id TEXT)')

print('Logging in...')
r = praw.Reddit(USERAGENT)
r.set_oauth_app_info(APP_ID, APP_SECRET, APP_URI)
r.refresh_access_information(APP_REFRESH)

def replybot():
    allcom=0
    link=0
    doesnotmatch=0
    longcom=0

    print('Searching %s.' % SUBREDDIT)
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = []
    if DO_SUBMISSIONS:
        posts += list(subreddit.get_new(limit=MAXPOSTS))
    if DO_COMMENTS:
        posts += list(subreddit.get_comments(limit=MAXPOSTS))
    posts.reverse()

    for post in posts:
        psub=post.subreddit.display_name
        if len(post.body.split()) < 20:
            if any(x in post.body for x in STOPWORDS):
                if post.body.count('-')<2:
                    if "http" not in post.body:
                        #print ("Searching for another the next comment")
                        # Anything that needs to happen every loop goes here.
                        pid = post.id

                        try:
                            pauthor = post.author.name
                        except AttributeError:
                            # Author is deleted. We don't care about this post.
                            continue

                        if pauthor.lower() == r.user.name.lower():
                            # Don't reply to yourself, robot!
                            print('Will not reply to myself.')
                            continue

                        if KEYAUTHORS != [] and all(auth.lower() != pauthor for auth in KEYAUTHORS):
                            # This post was not made by a keyauthor
                            continue

                        cur.execute('SELECT * FROM oldposts WHERE ID=?', [pid])
                        if cur.fetchone():
                            # Post is already in the database
                            continue

                        if isinstance(post, praw.objects.Comment):
                            pbody = post.body
                            for ch in ['(',')']:
                                if ch in pbody:
                                    pbody=pbody.replace(ch,"")
                        else:
                            pbody = '%s %s' % (post.title, post.selftext)
                        pbody = pbody.lower()

                        if not any(key.lower() in pbody for key in KEYWORDS):
                            # Does not contain our keyword
                            continue

                        cur.execute('INSERT INTO oldposts VALUES(?)', [pid])
                        sql.commit()
                        print('Replying to %s by %s in /r/%s' % (pid, pauthor,psub))
                        try:
                            if "\n" in pbody:
                                pbody=pbody[:pbody.index("\n")]
                            res = search_for_song(pbody)
                            if res:
                                # pbody=pbody[8:]
                                # pbody=pbody.replace("\n", "")
                                temp=pbody.lstrip()
                                temp=temp.rstrip()
                                temp=" ".join(temp.split())
                                temp=temp.title()
                                temp=temp.replace("?", "")
                                temp=temp.replace('"',"")
                                temp=temp.replace("#","")
                                temp=temp.replace(">","")
                                author, song_name = song_string_generator(pbody)
                                url = 'https://songlyrics.com/'+author+'/'+song_name+'-lyrics/'

                                post.reply("[**"+temp+"**]("+res+") \n ---- \n [**^^[Song ^^Lyrics]**] ("+url+") ^^| [**^^[Contact ^^me]**](https://www.reddit.com/message/compose?to=itailitai) ^^| ^^[**[Github]**](https://github.com/itailitai/Reddit-songs-to-youtube-bot) \n\n ^^Parent ^^commenter ^^can ^^reply ^^with ^^'delete'. ^^Will ^^also ^^delete ^^if ^^comment ^^score ^^is ^^-1 ^^or ^^less.")
                                # r.send_message('itailitai', 'SOME SUBJECT', 'Your bot just commented, check his profile : /u/youtubesong')

                        except praw.errors.Forbidden:
                            print('403 FORBIDDEN - is the bot banned from %s?' % post.subreddit.display_name)
                    else:
                        link+=1
                        allcom+=1

                else:
                    doesnotmatch+=1
                    allcom+=1
            else:
                doesnotmatch+=1
                allcom+=1
        else:
            longcom+=1
            allcom+=1
    print ("%s comments were completely ignored in this cycle:" % allcom)
    print("Too long comments: %s" % longcom)
    print ("Irrelevant comments: %s" % doesnotmatch)
    print ("Comments including a link: %s" % link)

def search_for_song(pbody):
    #print("in search_for_song")
    song=pbody
    if len(song)>0:
        song=song
        if song.isspace()==True or song=='':
            return False
        else:
            #HEADERS = {'User-Agent': 'Song checker - check if songs exists by searching this website, part of a bot for reddit'}
            author, song_name = song_string_generator(song)
            if author=='' or song_name=='':
                return False
            else:
                x=songexist(author,song_name,song)
                if "By" in song:
                    return x
                else:
                    if x:
                        return x
                    else:
                        return songexist(song_name,author,song)


def songexist(author,song_name,song):
    url = 'https://songlyrics.com/'+author+'/'+song_name+'-lyrics/'
    #page = requests.get(url, HEADERS)
    check=1
    while check==1:
        try:
            headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0' }
            req = urllib2.Request(url, None, headers)
            page= urllib2.urlopen(req)
            check=2
        except socket.error as error:
            pass
        except Exception:
            print('An error occured while trying to verify song existence')
            return False
    soup = BeautifulSoup(page.read(), "lxml")
    checklist=["Please check the spelling and try again","The page you're looking for cannot be found.","Do you like this album? Leave a review."]
    if any(x in soup.get_text() for x in checklist):
        print ("Song was not found in the database!")
        return False
    else:
        print ("Song was found in the database!")
        result=first_youtube(song)
        return result
def song_string_generator(song):
    #print("in song_string_generator")
    song=song

    check=["]","["]
    if any(x in song for x in check):
        author=''
        song_name=''
        return author, song_name
    else:
        song=song.rstrip('.')
        song=song.rstrip(':')
        song=song.rstrip('/')
        author,song_name= '',''
        if "-" in song:
            l=song.split('-', 1 )
            author=l[0]
            song_name=l[1]
        elif "by" in song:
            l=song.split('by', 1 )
            author=l[1]
            song_name=l[0]
        else:
            print ("song name invalid")
        song_name=" ".join(song_name.split())
        author=" ".join(author.split())
        if author == 'guns and roses':
            author="guns n' roses"

        if author == song_name:
            author=''
            song_name=''
            return author, song_name
        if author=="!" or song_name=="!":
            author,song_name= '',''
            return author, song_name
        song_name=song_name.replace("\n", "")
        author=author.replace("\n", "")
        author=author.replace(" ", "-")
        song_name=song_name.replace(" ", "-")
        author=author.replace("'", "-")
        song_name=song_name.replace("'", "-")
        song_name=song_name.replace("?", "-")
        author=author.replace("?", "-")
        author=author.replace("!", "-")
        song_name=song_name.replace("!", "-")
        song_name=song_name.rstrip()
        song_name=" ".join(song_name.split())
        if len(song_name) - song_name.count(' ') == 1 or len(author) - author.count(' ') == 1:
            return '',''
        return author, song_name


def first_youtube(textToSearch):
    reload(sys)
    sys.setdefaultencoding('UTF-8')
    query_string = textToSearch
    try:
        html_content = urllib.urlopen("http://www.youtube.com/results?search_query=" + query_string)
        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
        result="http://www.youtube.com/watch?v=" + search_results[0]
        return result
    except IOError:
        print ("IOError Occured while contacting Youtube!")

    except Exception:
        print ("A non IOError Occured while contacting Youtube!")
        return False

def deleteowncomments():
    print ("Comments deleting procedure has started")
    user=r.get_redditor("youtubesong")
    for c in user.get_comments(limit=None):
        if c.score < 0 :
	        c.delete()


def removebyreply():
    try:
        print(0)
        unread = r.get_unread(limit=None)
        print(1)
        for msg in unread:
            if msg.body.lower() == 'delete':
                try:
                    print(3)
                    id = msg.id
                    id = 't1_' + id
                    comment = r.get_info(thing_id=id)
                    comment= r.get_info(thing_id=comment.parent_id)
                    comment_parent = r.get_info(thing_id=comment.parent_id)
                    if msg.author.name == comment_parent.author.name or msg.author.name == 'itailitai':
                        print(4)
                        if "which was a reply to" not in comment.body:
                            comment.delete()
                            msg.reply('I have deleted [my comment](' + comment.permalink + '), which was a reply to [your comment](' + comment_parent.permalink + ').\n\nHave an amazing day, **' + str(msg.author.name) + '**!\n\n----- \n\n  [**^^[Contact ^^me]**](https://www.reddit.com/message/compose?to=itailitai) ^^| ^^[**[Github]**](https://github.com/itailitai/Reddit-songs-to-youtube-bot)')
                            msg.mark_as_read()
                        else:
                            msg.mark_as_read()
                    else:
                        print(5)
                        msg.mark_as_read()

                except Exception as e:
                    if (str(e) == "'NoneType' object has no attribute 'name'"):
                        print(6)
                        comment.delete()
                        msg.reply('I have deleted [my comment](' + comment.permalink + '), which was a reply to this [comment](' + comment_parent.permalink + ').\n\nHave an amazing day, **' + str(msg.author.name) + '**!\n\n----- \n\n  [**^^[Contact ^^me]**](https://www.reddit.com/message/compose?to=itailitai) ^^| ^^[**[Github]**](https://github.com/itailitai/Reddit-songs-to-youtube-bot)')
                    else:
                        print(7)
                        continue
                    msg.mark_as_read()
                    continue
    except Exception:
        print(8)
        None


cycles = 0
while True:
    try:
        replybot()
        cycles += 1
        removebyreply()
    except Exception as e:
        traceback.print_exc()
    if cycles >= CLEANCYCLES:
        print('Cleaning database')
        cur.execute('DELETE FROM oldposts WHERE id NOT IN (SELECT id FROM oldposts ORDER BY id DESC LIMIT ?)', [MAXPOSTS * 2])
        sql.commit()
        deleteowncomments()
        cycles = 0
    print('Running again in %d seconds \n' % WAIT)
    time.sleep(WAIT)
