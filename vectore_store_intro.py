from dotenv import load_dotenv
from langchain_core.documents import Document # Belgeleri temsil eder
from langchain_chroma import Chroma # Vektör veritabanı (Chroma). Kubernet, Docker ve Sunucu içine entgere edilerek kullanılabilir.
from langchain_ollama import OllamaEmbeddings  # Metinleri vektöre dönüştüren model
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate




load_dotenv()



# Arama yapılacak örnek belgeler
documents = [
    Document(
        page_content="Dogs are great companions, known for their loyalty and friendliness.", # Veri
        metadata={"source": "mammal-pets-doc"}, # Ekstra veri hakkında veri.
    ),
    Document(
        page_content="Cats are independent pets that often enjoy their own space.",
        metadata={"source": "mammal-pets-doc"},
    ),
    Document(
        page_content="Goldfish are popular pets for beginners, requiring relatively simple care.",
        metadata={"source": "fish-pets-doc"},
    ),
    Document(
        page_content="Parrots are intelligent birds capable of mimicking human speech.",
        metadata={"source": "bird-pets-doc"},
    ),
    Document(
        page_content="Rabbits are social animals that need plenty of space to hop around.",
        metadata={"source": "mammal-pets-doc"},
    ),
]


# Belgeler embedding (vektörel gösterim) ile vektör veritabanına dönüştürülüyor
vector_store = Chroma.from_documents(
    documents = documents,
    embedding = OllamaEmbeddings(model = "mistral")
)




"""if __name__ == "__main__":

    # Bir stringi arama
    #print(vector_store.similarity_search("dog"))

    # Bir stringi ara ve skorla
    #print(vector_store.similarity_search_with_score("dog"))

    # Vektor olarak arama
    #embedding = OllamaEmbeddings(model = "mistral").embed_query("Parrots are intelligent birds")
    embedding = OllamaEmbeddings(model = "mistral")
    vector = embedding.embed_query("Parrots are intelligent birds")
    print(vector_store.similarity_search_by_vector(vector))

"""


retriever = RunnableLambda(vector_store.similarity_search).bind(k = 1)


llm = ChatOllama(model = "mistral")


# LLM'e verilecek formatı belirliyoruz
message = """

Answer this question using the provided context only.

{question}

Context:

{context}

"""

# Chat için mesaj şablonu oluşturur
prompt = ChatPromptTemplate.from_messages(
    [
        ("human", message)
    ]
)


# → Retriever ile "context" alınır
# → Soru direkt geçer (Passthrough)
# → prompt doldurulur
# → LLM çalıştırılır
chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm


if __name__ == "__main__":
    # Retriever ile birden fazla şey aramak.
    #print(retriever.batch(["cats", "book"])) 


    # # Soru soruluyor ve model, retriever'dan gelen bilgiye göre yanıt veriyor

    response = chain.invoke("tell me about cats")

    print(response.content) # İçeriği döndürmesi için, content fonksiyonu kullanıldı.