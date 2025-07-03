import bs4
from dotenv import load_dotenv
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader # İnternetten veri çekmek için kullanılır.
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


"""
**** ToDo - List ****

1-) Retrieve data from the web source.

2-) Splitting data with text splitters.

3-) We will vectorize the data and add it to the Chroma vecto database

4-) Retriever will be created and some information will be requested from llm.

"""

load_dotenv()

llm = ChatOllama(model = "mistral")

# Part 1
# Set how and which parts of the data will be retrieved.
loader_data = WebBaseLoader(
    web_paths = ("https://lilianweng.github.io/posts/2023-06-23-agent/",), # birden fazla path verilebilir.
    bs_kwargs = dict(
        parse_only = bs4.SoupStrainer(
            class_ = ("post-content", "post-title", "post-content")

        )
    )
)

 

# Load data.
documents = loader_data.load()

# Making data readable
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)



# Part 2
# Splitting data with text splitters
text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
splits = text_splitter.split_documents(documents)




# Part 3 
# We will vectorize the data and add it to Chroma vector database
vectore_store = Chroma.from_documents(
    documents = splits,
    #embedding = OllamaEmbeddings(model = "all-minilm") daha hafif ve çok hızlı model, ama orta düzey kalite. Kısa metinler için ideal.
    embedding = OllamaEmbeddings(model = "nomic-embed-text") # Daha büyük ve daha az hızlı, ama daha yüksek kalite. Uzun belgeler için ideal.
)


# Part 4
# Retriever will be created
retriever = vectore_store.as_retriever()

# Creating rag prompt with hub
prompt = hub.pull("rlm/rag-prompt")

# Creating chain 
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)





if __name__ == "__main__":

    for chunk in rag_chain.stream("What is the Maximum Inner Product Search?"):
        print(chunk, end = "", flush = True) 