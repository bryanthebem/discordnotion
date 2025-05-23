from notion_client import Client
import os
from dotenv import load_dotenv
import json

# Carregar as variáveis de ambiente
load_dotenv()

import re
from datetime import datetime

class NotionIntegration:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.notion = Client(auth=self.token)
        

    def extract_database_id(self, url):
        match = re.search(r"([a-f0-9]{32})\?v=", url)
        if match:
            return match.group(1)  # Retorna apenas o ID do banco de dados
        return None

    def search_in_database(self, url, search_term, filter_property, property_type="rich_text"):
        # Extrair ID da URL
        database_id = self.extract_database_id(url)
        if not database_id:
            return "ID da base de dados não encontrado na URL."

        search_term = search_term.lower()
        # search_term = search_term.upper()

        # Nome da propriedade
        filter_criteria = {"property": filter_property}

        # Tipo da propriedade

        if property_type == "rich_text":  # Texto normal
            filter_criteria["rich_text"] = {"contains": search_term}

        elif property_type == "title":  # Título do card
            filter_criteria["title"] = {"contains": search_term}

        elif property_type == "multi_select":  # Filtro para multi_select
            print(f"\n Entrou no multi_select e realizando o filtro para chamar a API filter do Notion \n")
            
            resultados = []
            search_terms = [
                search_term.lower(),
                search_term.capitalize(),
                search_term.upper()
            ]

            try:
                for termo in search_terms:
                    print(f" Buscando com termo: {termo}")
                    filtro_temp = {
                        "property": filter_property,  
                        "multi_select": {"contains": termo}
                    }
                    result = self.notion.databases.query(database_id, filter=filtro_temp)
                    resultados.extend(result["results"])

                resultados_unicos = list({r["id"]: r for r in resultados}.values())
                print(f"\n  Resultados encontrados (únicos): {len(resultados_unicos)} páginas")
                return {"results": resultados_unicos}

            except Exception as e:
                return f"Erro ao buscar no Notion: {e}"

        elif property_type == "status":  # Status do card
            filter_criteria["status"] = {"equals": search_term}

        elif property_type == "select":  # select do card
            resultados = []
            search_terms = [
                search_term.lower(),
                search_term.capitalize(),
                search_term.upper()]
            
            try:
                for termo in search_terms:
                    print(f" Buscando com termo: {termo}")
                    filtro_temp = {
                        "property": filter_property,  
                        "select": {"equals": termo}
                    }
                    print(f" Filtro temporário: {filtro_temp}")
                    result = self.notion.databases.query(database_id, filter=filtro_temp)
                    resultados.extend(result["results"])

                resultados_unicos = list({r["id"]: r for r in resultados}.values())
                print(f"\n  Resultados encontrados (únicos): {len(resultados_unicos)} páginas")
                return {"results": resultados_unicos}
            # filter_criteria["select"] = {"equals": search_term}
            except Exception as e:
                return f"Erro ao buscar no Notion: {e}"

        elif property_type == "person":  # Envolvidos, associados a pessoas
            pessoa_id = self.search_id_person(database_id, search_term)
            print(f" ID da pessoa: {pessoa_id}")

            if pessoa_id:
                filter_criteria["people"] = {"contains": pessoa_id}
                print("🛠️ Filtro formatado:", filter_criteria)

                import json
                print("📩 JSON enviado para o Notion:")
                print(json.dumps(filter_criteria, indent=4))
            else:
                print("⚠️ Nenhuma pessoa encontrada com esse nome ou e-mail")

        elif property_type == "date":
            search_term = datetime.strptime(search_term, "%d/%m/%Y")
            search_term = search_term.strftime("%Y-%m-%d")
            filter_criteria["date"] = {"equals": search_term}

        elif property_type == "relation":
            filter_criteria["relation"] = {"contains": search_term}  # Pode precisar de ajustes


        if property_type not in ["multi_select", "select"]:
            # Executar a consulta no Notion
            try:
                print(f" Buscando no Notion com o filtro: {filter_criteria}")
                print(f" URL do banco de dados: {url}")
                print(f" ID do banco de dados: {database_id}")
                print(f"Filtro: {filter_criteria}")
                result = self.notion.databases.query(database_id, filter=filter_criteria)
                print(f"\n  Resultados encontrados: {len(result['results'])} páginas")
                print(f" Resultado da busca: {result}")
                return result
            except Exception as e:
                return f"Erro ao buscar no Notion: {e}"

    def get_database_properties(self, url):
        # Extrair ID da URL
        database_id = self.extract_database_id(url)
        if not database_id:
            return "ID da base de dados não encontrado na URL."

        # Obter propriedades da base de dados
        try:
            result = self.notion.databases.retrieve(database_id)
            properties = result['properties']
            return properties
        except Exception as e:
            return f"Erro ao obter propriedades: {e}"
        
    def search_id_person(self, notion_url, search_term):
        print(f"\n Buscando ID da pessoa com o termo: {search_term}")
        database = self.notion.databases.query(notion_url)  # Obter todos os registros
        for result in database["results"]:
            print
            envolvidos = result.get("properties", {}).get("Envolvida", {}).get("people", [])
            for pessoa in envolvidos:
                nome = pessoa.get("name", "").lower()
                email = pessoa.get("person", {}).get("email", "").lower()
                
                print(f"\n Nome: {nome}, E-mail: {email}\n")    

                if search_term.lower() in [nome, email]:  # Se nome ou email baterem
                    print(f"\n Search term: {search_term.lower()} \n")
                    return pessoa.get("id")  # Retorna o ID correto
                
        return None  

    def get_database_count(self, url):
        database_id = self.extract_database_id(url)
        if not database_id:
            return "ID da base de dados não encontrado na URL."

        try:
            result = self.notion.databases.query(database_id)
            return len(result['results'])
        except Exception as e:
            return f"Erro ao contar páginas: {e}"


    def insert_into_database(self, url, properties, child_properties=None):
        database_id = self.extract_database_id(url)
        if not database_id:
            return "ID da base de dados não encontrado na URL."

        # Inserir dados na base de dados
        try:
            response = self.notion.pages.create(
                parent={"database_id": database_id},
                properties=properties,
                children=child_properties if child_properties else []
            )
            return response
        except Exception as e:
            return f"Erro ao inserir dados: {e}"
        

    def validar_tipo_propriedade(self, url, nome_propriedade):
        try:
            response = self.notion.databases.retrieve(database_id=self.extract_database_id(url))
            propriedades = response["properties"]

            for nome, info in propriedades.items():
                if nome.lower() == nome_propriedade.lower():
                    return info["type"]

            return None  

        except Exception as e:
            print(f"Erro ao buscar tipo de propriedade: {e}")
            return None


    def montar_propriedade_por_tipo(self, nome_propriedade, tipo, valor):
        if tipo == "title":
            return {
                nome_propriedade: {
                    "title": [
                        {
                            "text": {"content": valor}
                        }
                    ]
                }
            }

        elif tipo == "rich_text":
            return {
                nome_propriedade: {
                    "rich_text": [
                        {
                            "text": {"content": valor}
                        }
                    ]
                }
            }

        elif tipo == "select":
            return {
                nome_propriedade: {
                    "select": {"name": valor}
                }
            }

        elif tipo == "multi_select":
            # adiciona múltiplos valores separados por vírgula
            tags = [{"name": tag.strip()} for tag in valor.split(",")]
            return {
                nome_propriedade: {
                    "multi_select": tags
                }
            }

        elif tipo == "status":
            return {
                nome_propriedade: {
                    "status": {"name": valor}
                }
            }

        elif tipo == "date":
            valor = datetime.strptime(valor, "%d/%m/%Y").strftime("%Y-%m-%d")
            # Formato esperado: YYYY-MM-DD
            return {
                nome_propriedade: {
                    "date": {"start": valor}
                }
            }

        elif tipo == "people":
            # id usuáro
            return {
                nome_propriedade: {
                    "people": [{"id": valor}]
                }
            }

        elif tipo == "checkbox":
            return {
                nome_propriedade: {
                    "checkbox": bool(valor)
                }
            }

        elif tipo == "number":
            return {
                nome_propriedade: {
                    "number": float(valor)
                }
            }

        else:
            print(f"Não existe o tipo de propriedade: {tipo}")
            return {}
