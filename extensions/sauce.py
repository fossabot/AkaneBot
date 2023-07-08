"""Search the source of a given image"""


import hikari as hk
import lightbulb as lb


import requests

from functions.utils import check_if_url

import dotenv

dotenv.load_dotenv()

SAUCENAO_KEY = os.getenv("SAUCENAO_KEY")

sauce_plugin = lb.Plugin(
    "plot", "A set of commands that are used to plot anime's trends"
)


@sauce_plugin.command
@lb.command("Find the Sauce", "Search the sauce of the image")
@lb.implements(lb.MessageCommand)
async def mangamenu(ctx: lb.MessageContext):

    
    if not check_if_url(link):
        await ctx.respond("There's nothing here to find the sauce of.")
        return

    params = {
        "api_key": SAUCENAO_KEY,
        "output_type": 2,
        "numres": 1,
        "url": ctx.options['target'].attachments[0].url
    }
    
    async with ctx.bot.d.aio_session.get(
        "https://saucenao.com/search.php?", params=params
    ) as res:

        if res.ok:
            res = await res.json()
            # print(res)
            data = res['results'][0]
            print(data)
            sauce = "😵"
            if 'source' in data['data'].keys():
                if 'ext_urls' in data['data'].keys():
                    sauce = f"[{data['data']['source']}]({data['data']['ext_urls'][0]})"
                else:
                    sauce = data['data']['source']
            else:
                sauce = data['data']['ext_urls'][0]
            await ctx.respond(
                embed=hk.Embed(
                    color=0x000000
                )
                .add_field("Similarity", data['header']['similarity'])
                .add_field("Source", sauce)
                .set_thumbnail(data['header']['thumbnail'])
                .set_author(name="Search results returned the follows: ")
                .set_footer(
                    text="Powered by: SauceNAO",
                    icon="https://i.imgur.com/2VRIEPR.png"
                )

            )


    # await find_sauce(ctx, "MANGA", ctx.options["target"].content)

@sauce_plugin.command
@lb.option(
    "link",
    "The link of the image to find the sauce of",
)
@lb.command(
    "sauce", "Show ya sauce for the image", pass_options=True, auto_defer=True
)
@lb.implements(lb.SlashCommand)
async def find_sauce(ctx: lb.Context, link: str) -> None:

    if not check_if_url(link):
        await ctx.respond("That's not a link <:AkanePoutColor:852847827826376736>")
        return

    params = {
        "api_key": SAUCENAO_KEY,
        "output_type": 2,
        "numres": 1,
        "url": link
    }
    
    async with ctx.bot.d.aio_session.get(
        "https://saucenao.com/search.php?", params=params
    ) as res:

        if res.ok:
            res = await res.json()
            # print(res)
            data = res['results'][0]
            print(data)
            sauce = "😵"
            if 'source' in data['data'].keys():
                if 'ext_urls' in data['data'].keys():
                    sauce = f"[{data['data']['source']}]({data['data']['ext_urls'][0]})"
                else:
                    sauce = data['data']['source']
            else:
                sauce = data['data']['ext_urls'][0]
            await ctx.respond(
                embed=hk.Embed(
                    color=0x000000
                )
                .add_field("Similarity", data['header']['similarity'])
                .add_field("Source", sauce)
                .set_thumbnail(data['header']['thumbnail'])
                .set_author(name="Search results returned the follows: ")
                .set_footer(
                    text="Powered by: SauceNAO",
                    icon="https://i.imgur.com/2VRIEPR.png"
                )

            )



@sauce_plugin.command
@lb.option(
    "link",
    "The link to check",
)
@lb.command(
    "pingu", "Check if site alive", pass_options=True, auto_defer=True
)
@lb.implements(lb.PrefixCommand)
async def pingu(ctx: lb.Context, link: str) -> None:
    
    if not check_if_url(link):
        await ctx.respond("That's... not a link <:AkanePoutColor:852847827826376736>")
        return

    if requests.get(link).ok:
        await ctx.respond(
            f"The site `{link}` is up and running ✅"
        )
    else:
        await ctx.respond(
            f"The site `{link}` is either down or has blocked the client ❌"
        )


def load(bot: lb.BotApp) -> None:
    """Load the plugin"""
    bot.add_plugin(sauce_plugin)


def unload(bot: lb.BotApp) -> None:
    """Unload the plugin"""
    bot.remove_plugin(sauce_plugin)