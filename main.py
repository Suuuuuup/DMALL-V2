import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio
import re

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='+', intents=intents)

COLOR_OPTIONS = {
    "Noir": discord.Color.default(),
    "Bleu": discord.Color.blue(),
    "Rouge": discord.Color.red(),
    "Vert": discord.Color.green()
}


def is_valid_url(url):
    regex = re.compile(r'^(?:http|ftp)s?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$')
    return re.match(regex, url) is not None

@bot.command()
async def dmall(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("T'a pas la permission")
        return

    embed = discord.Embed(title="DM All", description="pour dm all mec", color=discord.Color.default())
    embed.add_field(name="Instructions", value="Config ton dm all avec le menu déroulant")

    class DMConfig(View):
        def __init__(self):
            super().__init__(timeout=None)
            self.title = "Annonce"
            self.description = "Message par défaut"
            self.color = discord.Color.default()
            self.image_url = ""

        @discord.ui.select(placeholder="Choisis un truc à configurer", options=[
            discord.SelectOption(label="Titre", description="Définis le titre de l'embed"),
            discord.SelectOption(label="Description", description="Définis la description de l'embed"),
            discord.SelectOption(label="Couleur", description="Choisis une couleur pour l'embed"),
            discord.SelectOption(label="Image", description="Ajoute une URL d'image à l'embed")
        ])
        async def select_callback(self, interaction: discord.Interaction, select):
            selected_option = interaction.data["values"][0]
            if selected_option == "Titre":
                await interaction.response.send_message("Met un titre :", ephemeral=False)
                self.title = await self.wait_for_input(interaction)
                await interaction.followup.send("Titre mis à jour !", ephemeral=False)

            elif selected_option == "Description":
                await interaction.response.send_message("Met une description :", ephemeral=False)
                self.description = await self.wait_for_input(interaction)
                await interaction.followup.send("Description mise à jour !", ephemeral=False)

            elif selected_option == "Couleur":
                await interaction.response.send_message("Choisis une couleur : Noir, Bleu, Rouge, Vert", ephemeral=False)
                color_choice = await self.wait_for_input(interaction)
                if color_choice in COLOR_OPTIONS:
                    self.color = COLOR_OPTIONS[color_choice]
                    await interaction.followup.send("Couleur mise à jour !", ephemeral=False)
                else:
                    await interaction.followup.send("Euh... cette couleur existe pas.", ephemeral=False)

            elif selected_option == "Image":
                await interaction.response.send_message("Colle l'URL de l'image :", ephemeral=False)
                self.image_url = await self.wait_for_input(interaction)
                if is_valid_url(self.image_url):
                    await interaction.followup.send("Image mise à jour !", ephemeral=False)
                else:
                    await interaction.followup.send("L'URL de l'image n'est pas valide.", ephemeral=False)


            await interaction.delete_original_response()

        async def wait_for_input(self, interaction):
            def check(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel
            try:
                msg = await bot.wait_for("message", check=check, timeout=60)
                await msg.delete()  
                return msg.content
            except asyncio.TimeoutError:
                await interaction.followup.send("Trop tard, t'as mis trop de temps !", ephemeral=False)
                return ""

        @discord.ui.button(label="Go !", style=discord.ButtonStyle.green)
        async def send_dm(self, interaction: discord.Interaction, button):
            if not self.title or not self.description:
                await interaction.response.send_message("T'as oublié de mettre un titre ou une description !", ephemeral=False)
                return

            members = [member for member in ctx.guild.members if not member.bot]
            total = len(members)
            sent = 0

            
            embed = discord.Embed(title=self.title, description=self.description, color=self.color)
            if self.image_url:
                embed.set_image(url=self.image_url)

            await interaction.response.send_message(f"On envoie ça à {total} membres...", ephemeral=False)

            for member in members:
                try:
                    await member.send(embed=embed)
                    sent += 1
                except discord.Forbidden:
                    pass
                
            await ctx.send(f"Message envoyé à {sent}/{total} membres.")
            
            await interaction.delete_original_response()

    view = DMConfig()
    await ctx.send(embed=embed, view=view)

bot.run("TOKEN DU BOT")
