import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from notion_integration import NotionIntegration
notion_url = "https://www.notion.so/c7d253b06d114ee68266d6e769e29cf1?v=acad180d6a7f4965875044fc7cb0c723&pvs=4"

# Carregar variáveis de ambiente
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Inicializar bot
# Habilitar intents corretamente
intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix="!", intents=intents)

notion = NotionIntegration()


@bot.command(name="inserir_card")
async def insere_card(ctx, mensagem):
    # print(f" Comando recebido: {data_base_name} e Propriedades ({propriedades})")
    print(f" Comando recebido: {mensagem}")
    titulo, propriedades = extrair_info_mensagem_discord(mensagem)
    print(f" TÍTULO: {titulo} e PROPRIEDADES ({propriedades})")
    
@bot.command(name="busca_card")
async def busca_card(ctx, filtro, tipo, *, termo):
    print(f" Comando recebido: {filtro} ({tipo}) = {termo}")  

    from notion_integration import NotionIntegration
    notion = NotionIntegration()
    notion_url = "https://www.notion.so/c7d253b06d114ee68266d6e769e29cf1?v=acad180d6a7f4965875044fc7cb0c723&pvs=4"

    # Passando a propriedade e o tipo dela
    card = notion.search_in_database(notion_url, termo, filtro, tipo)

    print(f"CARD SENDO PPTRINTADO DENTRO DE BOT.PY: {card}")


    if not isinstance(card, dict) or 'results' not in card:
        print("Erro: card não é um dicionário válido ou não contém 'results'.")
        print(card)
        card = {"results": []}  # Garante que tenha um valor padrão

    count_retornados = len(card['results'])

    if count_retornados == 0:
        await ctx.send(f"❌ Nenhum resultado encontrado para **{termo}** na propriedade **{filtro}**.")
        return
    else:
        await ctx.send(f"🔎 {count_retornados} resultados encontrados.")

    print(f"🔎 {count_retornados} resultados encontrados.")


    mensagens = []

    variavel_que_pega_valor_card_results = card['results']
    print(f"\n PRINTANDO O CARD RESULTS: {variavel_que_pega_valor_card_results} \n")

    for result in card['results']:
        properties = result.get('properties', {})
        print(f"\n PRINTANDO O PROPERTIES: {properties} \n")

        nome = properties.get('Nome', {}).get('title', [])
        nome = nome[0].get('plain_text', 'Sem Nome') if nome else 'Sem Nome'
        autor = properties.get('Autor', {}).get('rich_text', [])
        autor = autor[0].get('plain_text', 'Sem Autor') if autor else 'Sem Autor'
        status = properties.get('Status', {}).get('status', {}).get('name', 'Sem Status')
        link = properties.get('Link', {}).get('url', 'Sem URL')

        lista_pessoas = []

        # Verifica se a chave "Envolvida" existe e contém a chave "people"
        if properties.get("Envolvida") and "people" in properties["Envolvida"]:
            lista_pessoas = properties["Envolvida"]["people"]

        if lista_pessoas:
            envolvidos = ", ".join(person.get("name", "Sem Nome") for person in lista_pessoas)
            envolvidos = ", ".join(person.get("name", "Sem Nome") for person in lista_pessoas)
            img_envolvidos = ", ".join(person.get("avatar_url", "Sem Nome") for person in lista_pessoas)
        else:
            envolvidos = "Nenhum envolvido registrado"



        criado_por = properties.get('Created by', {}).get('created_by', {}).get('name', 'Sem dados de criado por')

        relacionados = properties.get('Relacionado', {}).get('relation', [])
        if relacionados:
            relacionados = ", ".join(relation.get('name', 'Sem nome') for relation in relacionados)
        else:
            relacionados = "Nenhuma relação registrada"

        mensagem = (
            f"📌 **{nome}**\n"
            f"👤 **Autor:** {autor}\n"
            f"✅ **Status:** {status}\n"
            f"🔗 **[Acessar no Notion]({link})**\n"
            f"👥 **Envolvidos:** {envolvidos}\n"
            # f"👥 **Img envolvido:** {img_envolvidos}\n"
            f"🔗 **Relacionado a:** {relacionados}\n"
            f"📝 **Criado por:** {criado_por}\n"
        )

        mensagens.append(mensagem)

    for mensagem in mensagens:
        await ctx.send(mensagem)

@bot.command(name="num_cards")
async def num_cards(ctx):

    from notion_integration import NotionIntegration
    notion = NotionIntegration()
    notion_url = "https://www.notion.so/c7d253b06d114ee68266d6e769e29cf1?v=acad180d6a7f4965875044fc7cb0c723&pvs=4"

    database = notion.get_database_count(notion_url)

    # await ctx.send(resposta)
    await ctx.send(database)

# Evento quando o bot está pronto
@bot.event
async def on_ready():
    print(f"✅ {bot.user} está online!")

def extrair_info_mensagem_discord(mensagem):
    # Remove o comando inicial
    import re
    if mensagem.startswith("!inserir_card "):
        mensagem = mensagem[len("!inserir_card "):]

    partes = mensagem.split(",", 1)
    titulo = partes[0].strip()
    propriedades_brutas = partes[1].strip() if len(partes) > 1 else ""

    padrao = re.compile(r"(\w+):\s*(\([^)]+\)|[^,]+)")
    propriedades = {
        chave.strip(): valor.strip().strip("()")
        for chave, valor in padrao.findall(propriedades_brutas)
    }

    return titulo, propriedades

def criar_body_para_notion(database_id, titulo, propriedades, estrutura_db):
    from notion_integration import NotionIntegration
    notion = NotionIntegration()
    notion_url = "https://www.notion.so/c7d253b06d114ee68266d6e769e29cf1?v=acad180d6a7f4965875044fc7cb0c723&pvs=4"
    database_id = notion.extract_database_id(notion_url)

    body = {
        "parent": { "database_id": database_id },
        "properties": {}
    }

    # Adiciona o título
    body["properties"]["Nome"] = {
        "title": [
            {
                "text": { "content": titulo }
            }
        ]
    }

    # Itera pelas propriedades do comando e monta conforme o tipo esperado
    for nome_prop, valor in propriedades.items():
        tipo = estrutura_db.get(nome_prop)  # Exemplo: "multi_select", "rich_text", "date"
        if tipo:
            prop_formatada = notion.montar_propriedade_por_tipo(nome_prop, tipo, valor)
            body["properties"].update(prop_formatada)
        else:
            print(f"Tipo nçãp existenete: {nome_prop}")

    return body


# Rodar o bot
bot.run(DISCORD_TOKEN)
