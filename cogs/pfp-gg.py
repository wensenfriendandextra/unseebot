import discord
import requests
from bs4 import BeautifulSoup as bs4
from discord.ext import commands
from discord import app_commands

ROOT = "https://pfps.gg/pfps/"


def get_page(url):
    r = requests.get(url)
    return r.content


def scrape_page(url):
    pfps = []
    soup = bs4(get_page(url), "html.parser")
    scraped_pfps = soup.find_all("div", {"class": ["item-details", "text-center"]})
    for pfp in scraped_pfps:
        child = pfp.findChildren("a", recursive=False)
        if child:
            pfps.append(child[0])
    output = pfp_dict(pfps)
    return output


def pfp_dict(data):
    pfps = {}
    for pfp in data:
        pfp = str(pfp)
        if pfp.split('href="')[1].split('">')[0].split("/")[-1][0:4].isdigit():
            pfps[pfp.split('>')[1].split("</")[0]] = pfp.split('href="')[1].split('">')[0]
    return pfps


def get_download_url(url):
    return (url.replace('pfps.gg', 'PFPS.gg').replace('pfp', 'assets/pfps', 1) + '.png').lower()


def generate_embed(url, index, name, icon_url, non_dl_url):
    embed = discord.Embed(title=f'Result #{index + 1} [click to go to pfps.gg]', colour=discord.Colour.og_blurple(), url=non_dl_url)
    embed.set_author(name=f'Requested by {name}', icon_url=icon_url)
    embed.set_image(url=url)
    embed.set_footer(text='sourced from pfps.gg')

    return embed


class GetPfpCommand(commands.Cog):
    @app_commands.command(name='pfpsearch', description="scrapes pfp.gg for pfps that match your query")
    @app_commands.describe(query="the search term")
    async def _pfpsearch(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(thinking=True)
        urls = []
        embeds = []
        pages = []
        search = scrape_page(f"{ROOT}{query}")
        for i in search:
            pages.append(search[i])
            link = get_download_url(search[i])
            urls.append(link)
            if len(urls) > 2:
                break
        for url in urls:
            embeds.append(generate_embed(url, urls.index(url),
                                         f"{interaction.user.name}#{interaction.user.discriminator}",
                                         interaction.user.avatar.url, pages[urls.index(url)]))

        # loop again for the gifs bc I'm not going to scrape the website to find out what filetype it is
        for url in urls:
            embeds.append(generate_embed(url.replace('png','gif'), urls.index(url),
                                         f"{interaction.user.name}#{interaction.user.discriminator}",
                                         interaction.user.avatar.url, pages[urls.index(url)]))
        try:
            await interaction.followup.send(embeds=embeds)
        except Exception as err:
            if "error code: 50006" in str(err):
                await interaction.followup.send("no pfps were found for your query :(")
            else:
                print(err)


async def setup(bot):
    await bot.add_cog(GetPfpCommand(bot))
