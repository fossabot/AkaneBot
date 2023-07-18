"""Search the source of a given image"""


import os
import re

import dotenv
import hikari as hk
import lightbulb as lb
import requests

from extensions.ping import CustomView, GenericButton, KillButton, check_if_url

dotenv.load_dotenv()

SAUCENAO_KEY = os.getenv("SAUCENAO_KEY")

sauce_plugin = lb.Plugin(
    "plot", "A set of commands that are used to plot anime's trends"
)


@sauce_plugin.command
@lb.command("User pfp Sauce", "Sauce of user pfp")
@lb.implements(lb.UserCommand)
async def pfp_sauce(ctx: lb.UserContext):
    # try:
    params = {
        "api_key": SAUCENAO_KEY,
        "output_type": 2,
        "numres": 5,
        "url": ctx.options.target.avatar_url.url,
    }

    async with ctx.bot.d.aio_session.get(
        "https://saucenao.com/search.php?", params=params, timeout=3
    ) as res:
        if res.ok:
            res = await res.json()
            try:
                embed, view = await complex_parsing(ctx, res["results"][0])
                await ctx.respond(
                    embed=embed, components=view, flags=hk.MessageFlag.EPHEMERAL
                )
            except:
                embed, view = await simple_parsing(ctx, res["results"][0])
                await ctx.respond(
                    embed=embed, components=view, flags=hk.MessageFlag.EPHEMERAL
                )


@sauce_plugin.command
@lb.command("Find the Sauce", "Search the sauce of the image")
@lb.implements(lb.MessageCommand)
async def mangamenu(ctx: lb.MessageContext):
    try:
        url = find_url(ctx.options["target"].content)
        # print(url)
    except Exception as e:
        print(e)

    finally:
        if len(ctx.options["target"].attachments) == 0 and not url:
            await ctx.respond(
                "There's nothing here to find the sauce of <:AkaneSip:1095068327786852453>"
            )

        # if not url:
        if len(ctx.options["target"].attachments):
            url = ctx.options["target"].attachments[0].url

        # if not url:
        #     print("no url")
        # else:
        #     print(url)

    params = {
        "api_key": SAUCENAO_KEY,
        "output_type": 2,
        "numres": 5,
        "url": url,
    }

    async with ctx.bot.d.aio_session.get(
        "https://saucenao.com/search.php?", params=params, timeout=3
    ) as res:
        if res.ok:
            res = await res.json()
            try:
                embed, view = await complex_parsing(ctx, res["results"][0])
                view.add_item(KillButton(style=hk.ButtonStyle.SECONDARY, label="❌"))
                choice = await ctx.respond(embed=embed, components=view)
                await view.start(choice)
                await view.wait()
            except:
                embed, view = await simple_parsing(ctx, res["results"][0])
                view.add_item(KillButton(style=hk.ButtonStyle.SECONDARY, label="❌"))
                choice = await ctx.respond(embed=embed, components=view)
                await view.start(choice)
                await view.wait()


@sauce_plugin.command
@lb.option(
    "service",
    "The service to use to search for it",
    required=False,
    choices=["SauceNAO", "TraceMoe"],
)
@lb.option(
    "link",
    "The link of the image to find the sauce of",
)
@lb.command("sauce", "Show ya sauce for the image", pass_options=True, auto_defer=True)
@lb.implements(lb.SlashCommand)
async def find_sauce(ctx: lb.Context, link: str, service: str = None) -> None:
    if not check_if_url(link):
        await ctx.respond("That's not a link <:AkanePoutColor:852847827826376736>")
        return

    params = {"api_key": SAUCENAO_KEY, "output_type": 2, "numres": 5, "url": link}

    if service != "TraceMoe":
        res = await ctx.bot.d.aio_session.get(
            "https://saucenao.com/search.php?", params=params, timeout=3
        )
        if res.ok:
            res = await res.json()

            data = res["results"][0]
            try:
                embed, view = await complex_parsing(ctx, data)
                view.add_item(KillButton(style=hk.ButtonStyle.SECONDARY, label="❌"))
                choice = await ctx.respond(embed=embed, components=view)
                await view.start(choice)
                await view.wait()
            except Exception as e:
                print(e, "\n\n\n")
                embed, view = await simple_parsing(ctx, data)
                choice = view.add_item(
                    KillButton(style=hk.ButtonStyle.SECONDARY, label="❌")
                )
                await view.start(choice)
                await view.wait()
                await ctx.respond(embed=embed, components=view)

    else:
        try:
            async with ctx.bot.d.aio_session.get(
                "https://api.trace.moe/search", params={"url": link}, timeout=3
            ) as res:
                if res.ok:
                    res = (await res.json())["result"]

                    sauce = f"[{res[0]['filename']}](https://anilist.co/anime/{res[0]['anilist']})"

                    print(res[0]["similarity"] * 100)
                    view = CustomView(user_id=ctx.author.id)
                    view.add_item(KillButton(style=hk.ButtonStyle.SECONDARY, label="❌"))

                    choice = await ctx.respond(
                        embed=hk.Embed(color=0x000000)
                        .add_field(
                            "Similarity", f"{round(res[0]['similarity']*100, 2)}"
                        )
                        .add_field("Source", sauce)
                        .add_field("Episode", res[0]["episode"] or "1", inline=True)
                        .add_field(
                            "Timestamp",
                            f"{int(res[0]['from']//60)}m{int(res[0]['from']%60)}s - {int(res[0]['to']//60)}m{int(res[0]['to']%60)}s",
                            inline=True,
                        )
                        .set_thumbnail(res[0]["image"])
                        .set_author(name="Search results returned the follows: ")
                        .set_footer(
                            text="Powered by: Trace.Moe",
                        )
                    )
                    await view.start(choice)
                    await view.wait()
                else:
                    await ctx.respond("Couldn't find it.")
        except Exception as e:
            # print()
            print(e)


@sauce_plugin.command
@lb.option(
    "link",
    "The link to check",
)
@lb.command("pingu", "Check if site alive", pass_options=True, auto_defer=True)
@lb.implements(lb.PrefixCommand)
async def pingu(ctx: lb.Context, link: str) -> None:
    if not check_if_url(link):
        await ctx.respond("That's... not a link <:AkanePoutColor:852847827826376736>")
        return

    if requests.get(link).ok:
        await ctx.respond(f"The site `{link}` is up and running ✅")
    else:
        await ctx.respond(
            f"The site `{link}` is either down or has blocked the client ❌"
        )


async def complex_parsing(ctx: lb.Context, data: dict):
    sauce = "😵"
    if "MangaDex" in data["header"]["index_name"]:
        view = CustomView(user_id=ctx.author.id)
        try:
            if "mal_id" in data["data"].keys():
                view.add_item(
                    GenericButton(
                        style=hk.ButtonStyle.LINK,
                        emoji=hk.Emoji.parse("<:anilist:1127683041372942376>"),
                        url=(await al_from_mal(data["data"]["mal_id"]))["siteUrl"],
                    )
                )
            else:
                view.add_item(
                    GenericButton(
                        style=hk.ButtonStyle.LINK,
                        emoji=hk.Emoji.parse("<:anilist:1127683041372942376>"),
                        url=(await al_from_mal(name=data["data"]["source"]))["siteUrl"],
                    )
                )
        except Exception as e:
            print(e)
        view.add_item(
            GenericButton(
                style=hk.ButtonStyle.LINK,
                emoji=hk.Emoji.parse("<:mangadex:1128015134426677318>"),
                url=data["data"]["ext_urls"][0],
            )
        )
        return (
            hk.Embed(
                color=0x000000,
            )
            .add_field("Similarity", data["header"]["similarity"])
            .add_field("Source", f"{data['data']['source']} {data['data']['part']}")
            .add_field("Author", data["data"]["author"])
            .set_thumbnail(data["header"]["thumbnail"])
            .set_author(name="Search results returned the follows: ")
            .set_footer(
                text="Powered by: SauceNAO",
                icon="https://i.imgur.com/2VRIEPR.png",
            ),
            view,
        )
        # except Exception as e:
        #     print(e)

    elif "Anime" in data["header"]["index_name"]:
        # try:
        view = CustomView(user_id=ctx.author.id)
        if len(data["data"]["ext_urls"]) > 1:
            view.add_item(
                GenericButton(
                    style=hk.ButtonStyle.LINK,
                    emoji=hk.Emoji.parse("<:anilist:1127683041372942376>"),
                    url=data["data"]["ext_urls"][2],
                )
            )
        return (
            hk.Embed(
                color=0x000000,
            )
            .add_field("Similarity", data["header"]["similarity"])
            .add_field(
                "Source",
                data["data"]["source"],
            )
            .add_field("Episode", data["data"]["part"], inline=True)
            .add_field("Timestamp", data["data"]["est_time"], inline=True)
            .set_thumbnail(data["header"]["thumbnail"])
            .set_author(name="Search results returned the follows: ")
            .set_footer(
                text="Powered by: SauceNAO",
                icon="https://i.imgur.com/2VRIEPR.png",
            ),
            view,
        )
        # except Exception as e:
        #     print(e)

    elif "Danbooru" in data["header"]["index_name"]:
        # try:
        view = CustomView(user_id=ctx.author.id)
        view.add_item(
            GenericButton(
                style=hk.ButtonStyle.LINK,
                emoji=hk.Emoji.parse("<:danbooru:1130206873388326952>"),
                url=data["data"]["ext_urls"][0],
            )
        )
        view.add_item(
            GenericButton(
                style=hk.ButtonStyle.LINK,
                label="Original Image",
                url=data["data"]["source"],
            )
        )
        creator = ""
        if isinstance(data["data"]["creator"], str):
            creator = data["data"]["creator"]
        else:
            creator = ", ".join(data["data"]["creator"])
        return (
            hk.Embed(
                color=0x000000,
            )
            .add_field("Similarity", data["header"]["similarity"])
            .add_field("Artist", creator, inline=True)
            .add_field("Character(s)", data["data"]["characters"], inline=True)
            .add_field("Source Material", data["data"]["material"])
            .set_thumbnail(data["header"]["thumbnail"])
            .set_author(name="Search results returned the follows: ")
            .set_footer(
                text="Powered by: SauceNAO",
                icon="https://i.imgur.com/2VRIEPR.png",
            ),
            view,
        )
        # except Exception as e:
        #     print(e)

    elif "Pixiv" in data["header"]["index_name"]:
        # try:
        view = CustomView(user_id=ctx.author.id)
        view.add_item(
            GenericButton(
                style=hk.ButtonStyle.LINK,
                emoji=hk.Emoji.parse("<:pixiv:1130216490021425352>"),
                url=data["data"]["ext_urls"][0],
            )
        )
        return (
            hk.Embed(
                color=0x000000,
            )
            .add_field("Similarity", data["header"]["similarity"])
            .add_field(
                "Author",
                f"[{data['data']['member_name']}](https://www.pixiv.net/en/users/{data['data']['member_id']})",
            )
            .add_field("Title", data["data"]["title"])
            .set_thumbnail(data["header"]["thumbnail"])
            .set_author(name="Search results returned the follows: ")
            .set_footer(
                text="Powered by: SauceNAO",
                icon="https://i.imgur.com/2VRIEPR.png",
            ),
            view,
        )
        # except Exception as e:
        #     print(e)
    elif "H-Misc (E-Hentai)" in data["header"]["index_name"]:
        view = CustomView(user_id=ctx.author.id)
        # try:
        view.add_item(
            GenericButton(
                style=hk.ButtonStyle.LINK,
                emoji=hk.Emoji.parse("<:vndb_circle:1130453890307997747>"),
                label="VNDB",
                url=await vndb_url(data["data"]["source"]),
            )
        )

        return (
            hk.Embed(
                color=0x000000,
            )
            .add_field("Similarity", data["header"]["similarity"])
            .add_field("Source", data["data"]["source"])
            .add_field("Creator", ", ".join(data["data"]["creator"]))
            .set_thumbnail(data["header"]["thumbnail"])
            .set_author(name="Search results returned the follows: ")
            .set_footer(
                text="Powered by: SauceNAO",
                icon="https://i.imgur.com/2VRIEPR.png",
            ),
            view,
        )

    else:
        sauce = "😵"
        if "source" in data["data"].keys() and data["data"]["source"] != "":
            if "ext_urls" in data["data"].keys():
                sauce = f"[{data['data']['source']}]({data['data']['ext_urls'][0]})"
            else:
                sauce = data["data"]["source"]
        else:
            sauce = data["data"]["ext_urls"][0]

        embed = (
            hk.Embed(color=0x000000)
            .add_field("Similarity", data["header"]["similarity"])
            .add_field("Source", sauce)
            .set_thumbnail(data["header"]["thumbnail"])
            .set_author(name="Search results returned the follows: ")
            .set_footer(
                text="Powered by: SauceNAO", icon="https://i.imgur.com/2VRIEPR.png"
            )
        )

        for i, item in enumerate(data["data"].keys()):
            if item not in ["source", "ext_urls"] and not "id" in item:
                if i % 3:
                    embed.add_field(
                        sanitize_field(item), data["data"][item], inline=True
                    )
                else:
                    embed.add_field(sanitize_field(item), data["data"][item])

        return (embed, CustomView(user_id=ctx.author.id))


async def simple_parsing(ctx: lb.Context, data: dict):
    sauce = "😵"
    if "source" in data["data"].keys():
        if "ext_urls" in data["data"].keys():
            sauce = f"[{data['data']['source']}]({data['data']['ext_urls'][0]})"
        else:
            sauce = data["data"]["source"]
    else:
        sauce = data["data"]["ext_urls"][0]
    return (
        hk.Embed(color=0x000000)
        .add_field("Similarity", data["header"]["similarity"])
        .add_field("Source", sauce)
        .set_thumbnail(data["header"]["thumbnail"])
        .set_author(name="Search results returned the follows: ")
        .set_footer(
            text="Powered by: SauceNAO", icon="https://i.imgur.com/2VRIEPR.png"
        ),
        CustomView(user_id=ctx.author.id),
    )


def sanitize_field(name: str) -> str:
    return name.replace("_", " ").capitalize()


async def al_from_mal(mal_id: int = None, type: str = None, name: str = None) -> str:
    query = """
  query ($mal_id: Int, $search: String) { # Define which variables will be used (id)
    Media (idMal: $mal_id, search: $search, type: MANGA) {
      siteUrl
    }
  }

  """

    variables = {"mal_id": mal_id, "search": name}
    return (
        await (
            await sauce_plugin.bot.d.aio_session.post(
                "https://graphql.anilist.co",
                json={"query": query, "variables": variables},
                timeout=3,
            )
        ).json()
    )["data"]["Media"]


async def vndb_url(text):
    pattern = r"\[.*?\]"
    result_text = re.sub(pattern, "", text)

    url = "https://api.vndb.org/kana/vn"
    headers = {"Content-Type": "application/json"}
    data = {
        "filters": ["search", "=", result_text],
        "fields": "title",
        # "sort": "title"
    }
    req = await sauce_plugin.bot.d.aio_session.post(
        url, headers=headers, json=data, timeout=3
    )

    if not req.ok:
        return

    req = await req.json()
    return f"https://vndb.org/{req['results'][0]['id']}"
    # return result_text


pattern = r"https?://\S+|www\.\S+"

url_regex = re.compile(pattern)


def find_url(text):
    # Find the first occurrence of the pattern in the text
    match = url_regex.search(text)

    if match:
        return match.group()
    else:
        return None


def load(bot: lb.BotApp) -> None:
    """Load the plugin"""
    bot.add_plugin(sauce_plugin)


def unload(bot: lb.BotApp) -> None:
    """Unload the plugin"""
    bot.remove_plugin(sauce_plugin)
