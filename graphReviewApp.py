#####################################################################
# Name: Patrick Gonzalez
# Date: 09/23/2026
# Assignment: 4.5 Performance Assessment - Python Application
#             Accessing a Graph Database
# Purpose: Menu-driven Python application that connects to a local
#          Neo4j database, imports the review dataset as Category,
#          Product, Review, and Reviewer nodes with relationships
#          between them, and lets the user create their own nodes and
#          relationships, run count queries, and delete data.
#####################################################################

import json
from neo4j import GraphDatabase

# *Configure the database connection
print("Connecting to local Neo4j database...")
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password1")
driver = GraphDatabase.driver(URI, auth=AUTH)
session = driver.session()

DATASET_FILE = 'dataset_en_dev.json'
IMPORT_LIMIT = 500  # Only import a sample; each row issues several individual Cypher writes.


def import_dataset(path=DATASET_FILE, limit=IMPORT_LIMIT):
    # *Create Category, Product, Review, and Reviewer nodes from the imported JSON data,
    # then connect them with relationships
    print(f"Importing up to {limit} reviews from file...")
    categories = set()
    count = 0
    with open(path, 'r') as f:
        for line in f:
            if count >= limit:
                break
            data = json.loads(line)
            category = data["product_category"]
            if category not in categories:
                session.run("MERGE (:Category {name:$name})", name=category)
                categories.add(category)

            session.run("MERGE (:Product {name:$name})", name=data["product_id"])

            session.run(
                "CREATE (:Review {id:$id, title:$title, content:$content, stars:$stars})",
                id=data["review_id"], title=data["review_title"],
                content=data["review_body"], stars=int(data["stars"]),
            )

            session.run("MERGE (:Reviewer {name:$name})", name=data["reviewer_id"])

            # Reviewer -> Review
            session.run(
                "MATCH (reviewer:Reviewer {name:$reviewer}), (review:Review {id:$id}) "
                "CREATE (reviewer)-[:WROTE]->(review)",
                reviewer=data["reviewer_id"], id=data["review_id"],
            )
            # Product -> Category
            session.run(
                "MATCH (product:Product {name:$product}), (category:Category {name:$category}) "
                "MERGE (product)-[:CLASSIFIED_AS]->(category)",
                product=data["product_id"], category=category,
            )
            # Product -> Review
            session.run(
                "MATCH (product:Product {name:$product}), (review:Review {id:$id}) "
                "CREATE (product)-[:HAS_REVIEW]->(review)",
                product=data["product_id"], id=data["review_id"],
            )
            count += 1
    print(f"Imported {count} review(s) into the graph.\n")


# ---------------- Menu option 1: create a user-defined node ----------------

def create_node():
    # *Allow the user to create their own node with a Category, Product, Review, or Reviewer label
    label = input("Enter a label (Category, Product, Review, or Reviewer): ").strip()
    if label not in ("Category", "Product", "Review", "Reviewer"):
        print("Please enter Category, Product, Review, or Reviewer.")
        return
    if label == "Review":
        review_id = input("Review id: ").strip()
        title = input("Title: ").strip()
        content = input("Content: ").strip()
        stars = input("Stars: ").strip()
        session.run(
            "CREATE (:Review {id:$id, title:$title, content:$content, stars:$stars})",
            id=review_id, title=title, content=content, stars=int(stars) if stars.isdigit() else 0,
        )
    else:
        name = input("Name: ").strip()
        session.run(f"CREATE (:{label} {{name:$name}})", name=name)
    print(f"{label} node created.")


# ---------------- Menu option 2: create a user-defined relationship ----------------

def create_relationship():
    # *Allow the user to create their own relationship between Product and Category nodes,
    # or Product and Review nodes
    pair = input("Connect which pair? (Product-Category or Product-Review): ").strip()
    product_name = input("Product name: ").strip()
    if pair == "Product-Category":
        other_name = input("Category name: ").strip()
        query = (
            "MATCH (p:Product {name:$product}), (c:Category {name:$other}) "
            "CREATE (p)-[:CLASSIFIED_AS]->(c)"
        )
    elif pair == "Product-Review":
        other_name = input("Review id: ").strip()
        query = (
            "MATCH (p:Product {name:$product}), (r:Review {id:$other}) "
            "CREATE (p)-[:HAS_REVIEW]->(r)"
        )
    else:
        print("Please enter Product-Category or Product-Review.")
        return
    session.run(query, product=product_name, other=other_name)
    print("Relationship created.")


# ---------------- Menu option 3: count products per category ----------------

def count_products_in_category():
    # *Allow the user to enter a category name and see the count of Product nodes related to it
    category = input("Enter a category name: ").strip()
    result = session.run(
        "MATCH (:Product)-[:CLASSIFIED_AS]->(c:Category {name:$name}) RETURN COUNT(*) AS total",
        name=category,
    )
    print(f"'{category}' has {result.single()['total']} product(s).")


# ---------------- Menu option 4: count reviews per reviewer ----------------

def count_reviews_by_reviewer():
    # *Allow the user to enter a reviewer name (reviewer_id) and see the count of Review nodes
    # related to it
    reviewer = input("Enter a reviewer name (reviewer_id): ").strip()
    result = session.run(
        "MATCH (:Reviewer {name:$name})-[:WROTE]->(r:Review) RETURN COUNT(r) AS total",
        name=reviewer,
    )
    print(f"'{reviewer}' has written {result.single()['total']} review(s).")


# ---------------- Menu option 5: delete a category ----------------

def delete_category():
    # *Allow the user to enter a category name and delete the associated Category node
    category = input("Enter a category name to delete: ").strip()
    session.run("MATCH (c:Category {name:$name}) DETACH DELETE c", name=category)
    print(f"Category '{category}' deleted.")


# ---------------- Menu option 6: delete all relationships ----------------

def delete_all_relationships():
    # *Delete all relationships in the graph
    session.run("MATCH ()-[r]-() DELETE r")
    print("All relationships deleted.")


# ---------------- Menu option 7: delete all nodes ----------------

def delete_all_nodes():
    # *Delete all nodes in the graph
    session.run("MATCH (n) DELETE n")
    print("All nodes deleted.")


def print_menu():
    print("\n===== Amazon Neo4j Menu =====")
    print("1. Create your own node (Category/Product/Review/Reviewer)")
    print("2. Create your own relationship (Product-Category or Product-Review)")
    print("3. Count products in a category")
    print("4. Count reviews written by a reviewer")
    print("5. Delete a category")
    print("6. Delete all relationships")
    print("7. Delete all nodes")
    print("8. Exit")


def main():
    import_dataset()
    while True:
        print_menu()
        choice = input("Select an option (1-8): ").strip()
        if choice == "1":
            create_node()
        elif choice == "2":
            create_relationship()
        elif choice == "3":
            count_products_in_category()
        elif choice == "4":
            count_reviews_by_reviewer()
        elif choice == "5":
            delete_category()
        elif choice == "6":
            delete_all_relationships()
        elif choice == "7":
            delete_all_nodes()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid selection, please choose 1-8.")
    session.close()
    driver.close()


if __name__ == "__main__":
    main()
