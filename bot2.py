import discord
from discord.ext import commands
import os
from notion_integration import NotionIntegration

class DiscordBot(commands.Cog):
    
    def __init__(self):
        self.token = os.getenv("DISCORD_TOKEN")
        intents = discord.Intents.default()
        intents.message_content = True  
        # self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.notion_url = "https://www.notion.so/c7d253b06d114ee68266d6e769e29cf1?v=acad180d6a7f4965875044fc7cb0c723&pvs=4"
        bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
        bot.add_cog(DiscordBot(bot))
        bot.run(os.getenv("DISCORD_TOKEN"))


        # Instancia a integração com o Notion
        self.notion_integration = NotionIntegration()

        # Registra eventos
        self.bot.event(self.on_ready)
        self.bot.event(self.on_message)

        # Registra comandos
        # self.bot.add_command(self.oi)
        # self.bot.add_command(self.notion)
        # self.bot.add_command(self.buscar_resposta)
        # self.bot.add_command(self.buscar_card)
        # self.bot.add_command(self.buscar)
        self.bot.add_cog(self)


    async def on_ready(self):
        print(f"✅ Bot conectado como {self.bot.user}")

    async def on_message(self, message):
        print(f" Mensagem recebida: {message.content}")

        if self.bot.user.mention in message.content:
            print(" Bot foi mencionado!")
            await message.channel.send("Olá! Eu sou um bot 🤖")

        await self.bot.process_commands(message)  # Processa comandos corretamente

    @commands.command()
    async def oi(self, ctx):
        await ctx.send("Olá! Eu sou um bot 🤖")

    @commands.command()
    async def notion(self, ctx):
        notion_url = "https://www.notion.so/c7d253b06d114ee68266d6e769e29cf1?v=acad180d6a7f4965875044fc7cb0c723&pvs=4"
        count = self.notion_integration.get_database_count(notion_url)
        await ctx.send(f"Encontrei {count} páginas no Notion.")

    @commands.command()
    async def buscar_resposta(self, ctx, termo):
        notion_url = "https://www.notion.so/c7d253b06d114ee68266d6e769e29cf1?v=acad180d6a7f4965875044fc7cb0c723&pvs=4"
        result = self.notion_integration.search_in_database(notion_url, termo)
        
        if isinstance(result, dict) and result["results"]:
            resposta = result["results"][0]["properties"]["Resposta"]["rich_text"][0]["text"]["content"]
            await ctx.send(f"ncontrei a resposta: {resposta}")
        else:
            await ctx.send("Não encontrei nenhuma resposta para sua pergunta.")

    @commands.command()
    async def buscar_card(self, ctx, *, titulo: str):  # * permite múltiplas palavras no título
        notion_url = "https://www.notion.so/c7d253b06d114ee68266d6e769e29cf1?v=acad180d6a7f4965875044fc7cb0c723&pvs=4"

        print(f" Buscando card com título: {titulo}")  # LOG

        result = self.notion_integration.search_in_database(notion_url, titulo)
        print(f"🔎 Resultado da busca: {result}")  # LOG

        if isinstance(result, dict) and result.get("results"):
            card = result["results"][0]  
            propriedades = card.get("properties", {})

            propriedades_str = "\n".join([f"{campo}: {valor}" for campo, valor in propriedades.items()])
            
            await ctx.send(f"📌 Encontrei os dados para o card '{titulo}':\n{propriedades_str}")
        else:
            await ctx.send(f"❌ Não encontrei nenhum card com o título '{titulo}'.")


    @commands.command(name="buscar")
    async def buscar(self, ctx, *, titulo):
        print(f" Buscando pelo card: {titulo}...")
        await ctx.send(f" Buscando pelo card: `{titulo}`...")
        notion_url = "https://www.notion.so/c7d253b06d114ee68266d6e769e29cf1?v=acad180d6a7f4965875044fc7cb0c723"

        resultado = self.notion_integration.search_in_database(notion_url, titulo)

        print(f"🔎 Resultado da busca: {resultado}")  # LOG

        if not resultado["results"]:
            await ctx.send(" Nenhum resultado encontrado.")
            return

        # Pegando o primeiro resultado
        card = resultado["results"][0]

        print(f" Card encontrado: {card}")

        # Extraindo informações úteis
        nome = card["properties"]["Nome"]["title"][0]["plain_text"]
        autor = card["properties"]["Autor"]["rich_text"][0]["plain_text"]
        status = card["properties"]["Status"]["status"]["name"]
        link = card["properties"]["Link"]["url"]

        # Criando resposta formatada
        resposta = (
            f"📌 **{nome}**\n"
            f"👤 **Autor:** {autor}\n"
            f"📌 **Status:** {status}\n"
            f"🔗 **Link:** {link}"
        )

        await ctx.send(resposta)



    def run(self):
        self.bot.run(self.token)
