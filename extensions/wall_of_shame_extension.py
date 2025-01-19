import interactions
from interactions import Extension, SlashContext, OptionType, Embed, EmbedField, EmbedFooter, Color
from interactions.ext.paginators import Paginator
from database import RedisDB
from datetime import datetime

class WallOfShameExtension(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.db_wall_of_shame = RedisDB(db=6)

    @interactions.slash_command(name="wall_of_shame", description="Wall of Shame commands")
    async def wall_of_shame(self, ctx: SlashContext):
        pass

    @wall_of_shame.subcommand(name="view", description="View the wall of shame")
    @interactions.slash_option(
        name="username_or_user_id",
        description="Optional username or user ID to filter",
        required=False,
        opt_type=OptionType.STRING
    )
    async def view(self, ctx: SlashContext, username_or_user_id: str = None):
        if username_or_user_id:
            users = self.db_wall_of_shame.search_users(username_or_user_id)
        else:
            users = self.db_wall_of_shame.list_all_users_info().items()

        if not users:
            await ctx.send(f"No users found for '{username_or_user_id}'", ephemeral=True)
            return

        embeds = []
        for index, (user_id, user_info) in enumerate(users):
            username = user_info.get("username", "N/A")
            reason = user_info.get("reason", "N/A")
            proof_link = user_info.get("proof_link", "N/A")
            folder_id = user_info.get("folder_id", "N/A")

            embed = Embed(
                title=f"{username}",
                description="Here's some detailed information about the user:",
                color=Color.random(),
                fields=[
                    EmbedField(name="User ID", value=f"`{user_id}`", inline=True),
                    EmbedField(name="📜 Reason", value=f"*{reason}*", inline=False),
                    EmbedField(name="🔗 Proof Link", value=f"[Click Here]({proof_link})", inline=False),
                    EmbedField(name="Folder ID", value=f"`{folder_id}`", inline=True),
                ],
                footer=EmbedFooter(text=f"Wall of Shame | Page {index + 1} of {len(users)}"),
                timestamp=datetime.now().isoformat()
            )
            embeds.append(embed)

        paginator = Paginator.create_from_embeds(self.bot, *embeds)
        await paginator.send(ctx, ephemeral=True)

    @wall_of_shame.subcommand(name="add", description="Add a user to the wall of shame")
    @interactions.slash_option(
        name="username",
        description="Username of the user",
        required=True,
        opt_type=OptionType.STRING
    )
    @interactions.slash_option(
        name="reason",
        description="Reason for adding the user",
        required=True,
        opt_type=OptionType.STRING
    )
    @interactions.slash_option(
        name="image",
        description="Image attachment",
        required=False,
        opt_type=OptionType.ATTACHMENT
    )
    async def add(self, ctx: SlashContext, username: str, reason: str, image: interactions.Attachment = None):
        user_id = str(ctx.author.id)
        proof_link = image.url if image else "N/A"
        folder_id = "N/A"  # Placeholder for folder ID

        self.db_wall_of_shame.set_user(user_id, username, reason, proof_link, folder_id)

        await ctx.send(f"User {username} has been added to the wall of shame.", ephemeral=True)
