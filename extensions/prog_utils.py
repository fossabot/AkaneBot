"""The module to give you a static python interpreter"""
import subprocess

import hikari as hk
import lightbulb as lb

compiler_plugin = lb.Plugin(
    "Compiler", "An interpreter for Python", include_datastore=True
)
compiler_plugin.d.help = False

DSC_SYNTAX_GIST = (
    "https://gist.github.com/matthewzring"
    "/9f7bbfd102003963f9be7dbcf7d40e51#syntax-highlighting"
)


@compiler_plugin.command
@lb.option(
    "code", "The code to test", str, modifier=lb.commands.OptionModifier.CONSUME_REST
)
@lb.add_checks(lb.owner_only)
@lb.command(
    "e",
    "Test some code and see output/errors (python)",
    pass_options=True,
    aliases=["py", "exec"],
)
@lb.implements(lb.PrefixCommand)
async def compiler(ctx: lb.Context, code: str) -> None:
    """A function to return the output of your code.
    Use print() to print whatever output you desire

    Args:
        ctx (lb.Context): The message context
        code (str): The code to execute
    """

    if not (code.startswith("```py") and code.endswith("```")):
        await ctx.respond(
            (
                f"The entered code is not formatted correctly according to python."
                f" Consider referring : {hk.URL(DSC_SYNTAX_GIST)}."
            )
        )
        return

    with open("ntfc.py", "w+", encoding="utf-8") as codefile:
        codefile.write(code[5:-3])

    with subprocess.Popen(
        ["python3", "ntfc.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as result:
        output, error = result.communicate(timeout=12)
        print(output, error)
        if error:
            await ctx.respond(
                f"Process returned with error: ```{(str(error, 'UTF-8')).split('ntfc.py')[1][3:]}```"
            )
        else:
            if not output:
                await ctx.respond("This is the output ```        ```")
            else:
                await ctx.respond(
                    f"This is the output ```ansi\n{str(output, 'UTF-8')}```"
                )


def load(bot: lb.BotApp) -> None:
    """Load the plugin"""
    bot.add_plugin(compiler_plugin)


def unload(bot: lb.BotApp) -> None:
    """Unload the plugin"""
    bot.remove_plugin(compiler_plugin)
