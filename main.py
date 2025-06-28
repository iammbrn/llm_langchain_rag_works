from dotenv import load_dotenv
import os
from langchain_ollama import OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from fastapi import FastAPI
from langserve import add_routes

# .env dosyasını okumamnız sağlar.
load_dotenv()

# OllamaLLM modeli oluştururuz.
llm = OllamaLLM(
    model="mistral",          # 'model' parametresi kullanacağımız model ismi.
    temperature = 0.1,       # 'temperature' parametresi modelin ne kadar dopru sonuçlar vermesini belirler 0' a yaklaşınca dah doğru sonuçlar döndürür.
    base_url=os.getenv("OLLAMA_BASE_URL")) # 'base_url' parametresi Ollama'nın API sunucusuna erişim adresini sağlar.


"""system_messages = "Translate the following from Turkish to English" # Sistemden beklediğimiz görev komutu.
human_messages = "Sevgi ve muhabbet, bazen açması zaman alan, çekingen bir çiçek gibidir." # Göreve uygun örnek komut.

# Modele uygun mesaj listesi oluşturulur.
messages = [
        SystemMessage(content = system_messages),
        HumanMessage(content = human_messages)
    ]"""

# chat prompt şablonunu oluşturma.
system_prompt = "Translate the following into {language}"
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt), ("user", "{text}")
    ]
)

# Dönen sonucun string kısmını almamızı sağlayacak nesne.
parser = StrOutputParser() 

# chain, zinciri oluştur, zincirde önce prompt, sonra llm çalışır, daha sonra parser çalışır.  
chain = prompt | llm | parser

# API oluşturma.
app = FastAPI(title = "Transleted Chat Bot")
add_routes(app, chain, path="/translate")

if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host = "localhost", port = 8000)
    
    # print(chain.invoke({"language": "English", "text": "Sevgi her şeydir"})) # zincir uygulanır ve sonuç dödürülür.