Architecture Diagram
                    +---------------------------+
                    |       Client App          |
                    |  (Python / API / UI)      |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    |     Azure Cosmos DB       |
                    |   (SQL API - Products)    |
                    +-------------+-------------+
                                  |
                                  v
          ------------------------------------------------
          |               Products Container             |
          |----------------------------------------------|
          |  id (string)  | Partition Key = category     |
          |  name         | price                        |
          |  category     | stock                        |
          ------------------------------------------------



Step-by-Step Explanation
Step 1: Create Azure Cosmos DB Account

API type → SQL API

Throughput → 400 RU/s

Step 2: Create Database

Name → EcommerceDB

Step 3: Create Container

Container → Products
Partition Key → /category

Step 4: Connect Using Python

Use CosmosClient to authenticate and get container handle.

Step 5: Implement CRUD

Create → create_item()

Read → read_item()

Query → query_items()

Update → upsert_item()

Delete → delete_item()