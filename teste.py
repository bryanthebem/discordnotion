from notion_integration import NotionIntegration
from bot import extrair_info_mensagem_discord, criar_body_para_notion
notion = NotionIntegration()
notion_url = "https://www.notion.so/c7d253b06d114ee68266d6e769e29cf1?v=acad180d6a7f4965875044fc7cb0c723&pvs=4"

# resultado = notion.search_in_database(notion_url, "TV brasileira: da hegemonia à disputa com novas plataformas")
# count_resultado, resultado = notion.search_in_database(notion_url, "Concluído", "Status", "status")
# resultado = notion.search_in_database(notion_url, "VIVA CIÊNCIAS SOCIAIS", "Opção", "multi_select")
# print(f"\n {len(resultado)} resultados encontrados \n")
# print(resultado)

# body = {
#     "parent": {},
#     "properties": {},
#     "children": [],

# }

# tipo = notion.validar_tipo_propriedade(notion_url, "Opção")
# tipo_2 = notion.validar_tipo_propriedade(notion_url, "Nome")
# tipo_3 = notion.validar_tipo_propriedade(notion_url, "Status")
# print(tipo)  
# print(tipo_2)
# print(tipo_3)
# nova_prop = notion.montar_propriedade_por_tipo("Opção", tipo, "Importante, Urgente")
# nova_prop_2 = notion.montar_propriedade_por_tipo("Nome", tipo_2, "Nova Demanda")
# nova_prop_3 = notion.montar_propriedade_por_tipo("Status", tipo_3, "Concluído")

# # Inserindo no body
# body["properties"].update(nova_prop)
# body["properties"].update(nova_prop_2)
# body["properties"].update(nova_prop_3)
# print(body)



mensagem = "!inserir_card Lista de Leituras, Nome: Nova demanda externa, Envolvida: giovanna souza, Autor: Jenny Han, Date: 12/04/2025, Opção: (TAG1, TAG2)"

titulo, propriedades = extrair_info_mensagem_discord(mensagem)


print(f"\nTítulo: {titulo}")
print(f"Propriedades: {propriedades}")

estrutura_db = {}

for chave, valor in propriedades.items():
    tipo = notion.validar_tipo_propriedade(notion_url, chave)
    if tipo == 'people':
        print(f"\nTipo: {tipo}")
        print(f"\nChave: {chave}")
        print(f"\nValor: {valor}")
        id_pessoa = notion.search_id_person(notion_url, valor)
        print(f"\nID da pessoa: {id_pessoa}")
        propriedades[chave] = id_pessoa
    estrutura_db[chave] = tipo

print(f"\n Propriedades após o for: {propriedades}")

print(f"\nEstrutura do banco de dados: {estrutura_db}")

database_id = notion.extract_database_id(notion_url)

body = criar_body_para_notion(database_id, titulo, propriedades, estrutura_db)

print(f"\nBody para Notion: {body}")


