import datetime
import json
from typing import Optional, Sequence, Union
from urllib.parse import urlparse

import feedparser
import hikari as hk
import miru
from miru.ext import nav


class CustomNavi(nav.NavigatorView):
    def __init__(
        self,
        *,
        pages: Sequence[Union[str, hk.Embed, Sequence[hk.Embed]]],
        buttons: Optional[Sequence[nav.NavButton]] = None,
        timeout: Optional[Union[float, int, datetime.timedelta]] = 180.0,
        user_id: hk.Snowflake = None,
    ) -> None:
        self.user_id = user_id
        super().__init__(pages=pages, buttons=buttons, timeout=timeout)

    async def on_timeout(self) -> None:
        await self.message.edit(components=[])
        if self.get_context(self.message).bot.d.chapter_info[self.message_id]:
            self.get_context(self.message).bot.d.chapter_info[self.message_id] = None
            print("Cleared cache\n\n\n")


class CustomView(miru.View):
    def __init__(
        self,
        *,
        autodefer: bool = True,
        timeout: Optional[Union[float, int, datetime.timedelta]] = 180.0,
        user_id: hk.Snowflake = None,
    ) -> None:
        self.user_id = user_id
        super().__init__(autodefer=autodefer, timeout=timeout)


def check_if_url(link: str) -> bool:
    parsed = urlparse(link)
    if parsed.scheme and parsed.netloc:
        return True
    return False


def rss2json(url):
    """
    rss atom to parsed json data
    supports google alerts
    """

    item = {}
    feedslist = []
    feed = {}
    feedsdict = {}
    # parsed feed url
    parsedurl = feedparser.parse(url)

    # feed meta data
    feed["status"] = "ok"
    feed["version"] = parsedurl.version
    if "updated" in parsedurl.feed.keys():
        feed["date"] = parsedurl.feed.updated
    if "title" in parsedurl.feed.keys():
        feed["title"] = parsedurl.feed.title
    if "image" in parsedurl.feed.keys():
        feed["image"] = parsedurl.feed.image
    feedsdict["data"] = feed

    # feed parsing
    for fd in parsedurl.entries:
        if "title" in fd.keys():
            item["title"] = fd.title

        if "link" in fd.keys():
            item["link"] = fd.link

        if "summary" in fd.keys():
            item["summary"] = fd.summary

        if "published" in fd.keys():
            item["published"] = fd.published

        if "storyimage" in fd.keys():
            item["thumbnail"] = fd.storyimage

        if "media_content" in fd.keys():
            item["thumbnail"] = fd.media_content

        if "tags" in fd.keys():
            if "term" in fd.tags:
                item["keywords"] = fd.tags[0]["term"]

        feedslist.append(item.copy())

    feedsdict["feeds"] = feedslist

    return json.dumps(feedsdict)

def verbose_timedelta(delta):
    d = delta.days
    h, s = divmod(delta.seconds, 3600)
    m, s = divmod(s, 60)
    labels = ["day", "hour", "minute", "second"]
    dhms = [
        "%s %s%s" % (i, lbl, "s" if i != 1 else "")
        for i, lbl in zip([d, h, m, s], labels)
    ]
    for start in range(len(dhms)):
        if not dhms[start].startswith("0"):
            break
    for end in range(len(dhms) - 1, -1, -1):
        if not dhms[end].startswith("0"):
            break
    return ", ".join(dhms[start : end + 1])



def iso_to_timestamp(iso_date):
    try:
        return int(datetime.datetime.fromisoformat(iso_date[:-1] + '+00:00').astimezone().timestamp())
    
    except ValueError: # Incase the datetime is not in the iso format, return it as is
        return iso_date

    
class PeristentViewTest(miru.View):
    def __init__(self) -> None:
        super().__init__(autodefer=True, timeout=None)
