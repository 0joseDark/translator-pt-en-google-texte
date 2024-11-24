import requests
import urllib.parse
import time
from typing import Optional

class GoogleTranslator:
    def __init__(self):
        self.base_url = "https://translate.googleapis.com/translate_a/single"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'pt') -> Optional[str]:
        """
        Traduz o texto usando o Google Translate
        
        Args:
            text: Texto para traduzir
            source_lang: Idioma de origem (padrão: 'en')
            target_lang: Idioma de destino (padrão: 'pt')
            
        Returns:
            Texto traduzido ou None em caso de erro
        """
        try:
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            
            # Codifica os parâmetros da URL
            encoded_params = urllib.parse.urlencode(params)
            url = f"{self.base_url}?{encoded_params}"
            
            # Faz a requisição
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Processa a resposta
            result = response.json()
            if result and isinstance(result[0], list):
                translated_text = ''
                for item in result[0]:
                    if item[0]:
                        translated_text += item[0]
                return translated_text
            
            return None
            
        except requests.RequestException as e:
            print(f"Erro na requisição: {e}")
            return None
        except (IndexError, KeyError, ValueError) as e:
            print(f"Erro ao processar resposta: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return None

def main():
    # Exemplo de uso
    translator = GoogleTranslator()
    
    # Lista de textos para traduzir
    texts = [
        "Hello, how are you?",
        "This is a test translation",
        "Good morning!",
    ]
    
    print("Iniciando traduções...")
    for text in texts:
        # Adiciona um pequeno delay entre as requisições para evitar bloqueios
        time.sleep(1)
        
        translated = translator.translate(text)
        if translated:
            print(f"\nOriginal: {text}")
            print(f"Tradução: {translated}")
        else:
            print(f"\nFalha ao traduzir: {text}")

if __name__ == "__main__":
    main()