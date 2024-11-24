- ![Babel](![Babel](https://github.com/0joseDark/translator-pt-en-google-texte/blob/main/image/torre-babel.jpg)
# translator pt to en google texte
- pip install googletrans==4.0.0-rc1
- ![translator](![translator](https://github.com/0joseDark/translator-pt-en-google-texte/blob/main/image/translator-pt-en.jpg)
- -
O **módulo `googletrans`** (ou sua versão atualizada chamada `googletrans==4.0.0-rc1`) é uma biblioteca Python usada para traduzir texto automaticamente utilizando o **Google Translate**. 

Ele é fácil de usar e suporta uma grande variedade de idiomas. É útil para traduzir strings, detectar idiomas e até trabalhar com grandes volumes de texto em scripts ou aplicações.

---

### **Instalação do `googletrans`**

1. Certifique-se de ter o Python instalado.
2. Execute o comando no terminal para instalar:

```bash
pip install googletrans==4.0.0-rc1
```

---

### **Recursos Principais**
1. **Tradução de texto**: Permite traduzir textos entre dois idiomas.
2. **Detecção de idioma**: Detecta o idioma de entrada automaticamente.
3. **Idiomas suportados**: Dá uma lista de todos os idiomas reconhecidos pelo Google Translate.

---

### **Exemplo 1: Tradução Simples**

```python
from googletrans import Translator

# Criar um objeto tradutor
tradutor = Translator()

# Texto para traduzir
texto = "Hello, how are you?"

# Traduzir para português
traducao = tradutor.translate(texto, src='en', dest='pt')

print(f"Texto original: {texto}")
print(f"Tradução: {traducao.text}")
```

**Saída**:
```
Texto original: Hello, how are you?
Tradução: Olá, como você está?
```

---

### **Exemplo 2: Detectar o Idioma**

```python
from googletrans import Translator

# Criar um objeto tradutor
tradutor = Translator()

# Texto para detectar o idioma
texto = "Bonjour tout le monde"

# Detectar o idioma
detectar = tradutor.detect(texto)

print(f"Texto: {texto}")
print(f"Idioma detectado: {detectar.lang} com confiança de {detectar.confidence * 100}%")
```

**Saída**:
```
Texto: Bonjour tout le monde
Idioma detectado: fr com confiança de 99.0%
```

---

### **Exemplo 3: Listar Idiomas Suportados**

```python
from googletrans import LANGUAGES

# Listar todos os idiomas suportados
for codigo, nome in LANGUAGES.items():
    print(f"{codigo}: {nome}")
```

**Saída** (Exemplo):
```
af: afrikaans
ar: arabic
en: english
pt: portuguese
es: spanish
fr: french
```

---

### **Exemplo 4: Tradução de Um Texto Longo**

```python
from googletrans import Translator

# Criar um objeto tradutor
tradutor = Translator()

# Texto longo para traduzir
texto_longo = """
Artificial Intelligence (AI) is a branch of computer science dealing with the simulation of intelligent behavior in computers.
"""

# Traduzir para português
traducao = tradutor.translate(texto_longo, src='en', dest='pt')

print(f"Texto traduzido:\n{traducao.text}")
```

**Saída**:
```
Texto traduzido:
A Inteligência Artificial (IA) é um ramo da ciência da computação que lida com a simulação de comportamento inteligente em computadores.
```

---

### Observação Importante:
O `googletrans` pode, em alguns casos, apresentar limitações se houver alterações na API do Google Translate. Se isso ocorrer, você pode:
1. **Usar alternativas**: Como `translatepy` ou a API oficial paga do Google Cloud.
2. **Customizar**: Criar uma integração própria via requisições HTTP para o site.



 
