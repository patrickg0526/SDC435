SDC435

patgon2554

redisMenuApp.py - Menu-driven Python CRUD application that connects to a local Redis key-value database, imports the review dataset, and lets the user create, read, update, and delete sets interactively.

mongoReviewApp.py - Menu-driven Python CRUD application that connects to a local MongoDB Amazon.ReviewData collection, imports the review dataset, and lets the user create, read (with find_one and advanced find filters), update, and delete review documents interactively.

cassandraReviewApp.py - Menu-driven Python CRUD application that connects to a local Cassandra database, creates an Amazon keyspace with Reviews and ProductCategories tables, imports the review dataset, and lets the user display distinct categories, count reviews by star rating and category, run custom CQL SELECT statements, add/remove table columns, and drop the tables and keyspace interactively.

graphReviewApp.py - Menu-driven Python CRUD application that connects to a local Neo4j graph database, imports the review dataset as Category, Product, Review, and Reviewer nodes with relationships between them, and lets the user create their own nodes and relationships, count products per category, count reviews per reviewer, delete a category, and delete all relationships/nodes interactively.
