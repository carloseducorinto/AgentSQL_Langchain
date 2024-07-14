from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os


class Database:
    
    def connect_to_database(self, host, user, password, port, database):
        db_uri = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'
        return SQLDatabase.from_uri(db_uri)

     
    def get_sql_chain(self, db):
        template = """
        You are a data analyst at a derivatives trading company. You have been tasked with analyzing the company's 
        trading data to identify trends and patterns. 
        Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation
        history into account when writing the query.
        
        <SCHEMA>{schema}</SCHEMA>
        
        Conversation History: {chat_history}
        
        Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
        
        For example:
        Question: Find all market data entries recorded on 2024-03-28
        SQL Query: SELECT * FROM market_data WHERE market_date = '2024-03-28';
        Question: List all clients who are of type 'Coporate
        SQL Query:SELECT * FROM clients WHERE client_type = 'Coporate';
        Question: Find the top clients by transaction volume for each product
        SQL Query: SELECT derivative_products.product_name, clients.client_name, SUM(transactions.quantity) AS total_quantity FROM transactions JOIN clients ON transactions.client_id = clients.client_id JOIN derivative_products ON transactions.product_id = derivative_products.product_id GROUP BY derivative_products.product_name, clients.client_name ORDER BY derivative_products.product_name, total_quantity DESC;
        
        Your turn:
        
        Question: {question}
        SQL Query:       
        
        """
        prompt = ChatPromptTemplate.from_template(template)

        llm = ChatOpenAI(model='gpt-3.5-turbo', api_key=os.getenv('OPENAI_API_KEY'), temperature=0.1)
        
        def get_schema(_):
            print('schema : ' + db.get_table_info())
            return db.get_table_info()

        return(
            RunnablePassthrough.assign(schema=get_schema)
            | prompt
            | llm
            | StrOutputParser()
        )


    def get_response(self, user_query: str, db: SQLDatabase, chat_history: list):
        
        sql_chain = Database.get_sql_chain(self, db)
        
        template = """ 
        You are a data analyst at a derivatives trading company. You are interacting with a user who is asking
        questions about the company's trading data. Based on the table schema below, question, sql query, and 
        sql response, write a natural language response.
        
        <SCHEMA>{schema}</SCHEMA>
        
        Conversation History: {chat_history}
        SQL Query: <SQL>{query}</SQL>
        User question: {question}
        SQL Response: {response}      
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        llm = ChatOpenAI(model='gpt-3.5-turbo', api_key=os.getenv('OPENAI_API_KEY'), temperature=0.1)
        
        chain = (
            
            RunnablePassthrough.assign(query=sql_chain).assign(
                schema = lambda _: db.get_table_info(),
                response=lambda vars: db.run(vars["query"])
            )
            | prompt
            | llm
            | StrOutputParser()
        )
    
        
        
        return chain.invoke({
            "question": user_query,
            "chat_history": chat_history
        }
        )