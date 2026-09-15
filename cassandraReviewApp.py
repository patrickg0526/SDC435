#####################################################################
# Name: Patrick Gonzalez
# Date: 09/15/2026
# Assignment: 3.5 Performance Assessment - Python Application
#             Accessing a Column Family Database
# Purpose: Menu-driven Python application that connects to a local
#          Cassandra database, creates an Amazon keyspace with
#          Reviews and ProductCategories tables, imports the review
#          dataset, and lets the user perform CRUD operations,
#          run ad-hoc CQL SELECT statements, alter table columns,
#          and drop tables/keyspace.
#####################################################################

import json
from cassandra.cluster import Cluster

# *Configure the database connection
print("Connecting to local Cassandra database...")
cluster = Cluster()
session = cluster.connect()

DATASET_FILE = 'dataset_en_dev.json'
IMPORT_LIMIT = 2000  # Only import a sample; the full dataset is 5000 rows.


def create_keyspace_and_tables():
    # *Create a new keyspace in the Cassandra database named Amazon
    keyspace = '''
        CREATE KEYSPACE IF NOT EXISTS Amazon WITH replication =
        {'class':'SimpleStrategy','replication_factor':1};
        '''
    session.execute(keyspace)
    session.execute('USE Amazon;')
    session.set_keyspace('amazon')

    # *Create a new table in the Cassandra database named Reviews
    reviewsTable = '''
        CREATE TABLE IF NOT EXISTS Reviews(
        review_id text PRIMARY KEY,
        product_id text,
        reviewer_id text,
        stars int,
        review_body text,
        review_title text,
        product_category text
        );
        '''
    session.execute(reviewsTable)

    # *Create a new table in the Cassandra database named ProductCategories
    categoriesTable = '''
        CREATE TABLE IF NOT EXISTS ProductCategories(
        product_id text,
        stars int,
        language text,
        product_category text,
        PRIMARY KEY((product_category), stars, product_id)
        );
        '''
    session.execute(categoriesTable)


def import_dataset(path=DATASET_FILE, limit=IMPORT_LIMIT):
    # *Insert data from the JSON file into the Reviews and ProductCategories tables
    print(f"Importing up to {limit} reviews from file...")
    insertReviews = '''
        INSERT INTO Reviews (review_id, product_id, reviewer_id, stars,
        review_body, review_title, product_category)
        VALUES(%s, %s, %s, %s, %s, %s, %s);
        '''
    insertCategories = '''
        INSERT INTO ProductCategories (product_id, stars, language, product_category)
        VALUES(%s, %s, %s, %s);
        '''
    count = 0
    with open(path, 'r') as f:
        for line in f:
            if count >= limit:
                break
            data = json.loads(line)
            session.execute(insertReviews, [
                data["review_id"], data["product_id"], data["reviewer_id"],
                int(data["stars"]), data["review_body"], data["review_title"],
                data["product_category"],
            ])
            session.execute(insertCategories, [
                data["product_id"], int(data["stars"]), data["language"],
                data["product_category"],
            ])
            count += 1
    print(f"Imported {count} review(s) into Amazon.Reviews and Amazon.ProductCategories.\n")


def show_distinct_categories():
    # *Display all distinct product categories from the ProductCategories table
    query = 'SELECT DISTINCT product_category FROM ProductCategories;'
    results = session.execute(query)
    categories = sorted({row.product_category for row in results})
    print(f"\n{len(categories)} distinct product categories:")
    for cat in categories:
        print(" -", cat)


def count_high_star_reviews():
    # *Display the count of 4-star and higher reviews for a user-entered product category
    category = input("Enter a product category: ").strip()
    query = '''SELECT COUNT(*) FROM ProductCategories WHERE product_category = %s
            AND stars >= 4 ALLOW FILTERING;'''
    result = session.execute(query, [category])
    print(f"4-star and higher reviews for '{category}': {result.one().count}")


def count_one_star_reviews():
    # *Display the count of 1-star reviews for a user-entered product category
    category = input("Enter a product category: ").strip()
    query = '''SELECT COUNT(*) FROM ProductCategories WHERE product_category = %s
            AND stars = 1 ALLOW FILTERING;'''
    result = session.execute(query, [category])
    print(f"1-star reviews for '{category}': {result.one().count}")


def run_custom_select():
    # *Allow the user to type in and execute CQL SELECT statements
    cql = input("Enter a CQL SELECT statement (without trailing semicolon): ").strip()
    if not cql.lower().startswith("select"):
        print("Only SELECT statements are allowed here.")
        return
    try:
        results = session.execute(cql + ";" if not cql.endswith(";") else cql)
        count = 0
        for row in results:
            print(row)
            count += 1
            if count >= 25:
                print("... (showing first 25 rows)")
                break
        if count == 0:
            print("No rows returned.")
    except Exception as e:
        print(f"Error running query: {e}")


def alter_columns():
    # *Allow the user to add and remove columns from the Reviews and ProductCategories tables
    table = input("Which table? (Reviews/ProductCategories): ").strip()
    if table.lower() not in ("reviews", "productcategories"):
        print("Please enter 'Reviews' or 'ProductCategories'.")
        return
    action = input("Type 'add' to add a column or 'remove' to drop a column: ").strip().lower()
    column = input("Enter the column name: ").strip()
    if action == "add":
        col_type = input("Enter the column type (e.g. text, int): ").strip()
        query = f"ALTER TABLE {table} ADD {column} {col_type};"
    elif action == "remove":
        query = f"ALTER TABLE {table} DROP {column};"
    else:
        print("Unrecognized action.")
        return
    try:
        session.execute(query)
        print(f"Table '{table}' altered successfully.")
    except Exception as e:
        print(f"Error altering table: {e}")


def delete_tables():
    # *Allow the user to delete the Reviews and ProductCategories tables
    confirm = input("Type YES to confirm dropping the Reviews and ProductCategories tables: ").strip()
    if confirm == "YES":
        session.execute("DROP TABLE IF EXISTS Reviews;")
        session.execute("DROP TABLE IF EXISTS ProductCategories;")
        print("Both tables have been dropped.")
    else:
        print("Cancelled; tables were not dropped.")


def delete_keyspace():
    # *Allow the user to delete the Amazon keyspace
    confirm = input("Type YES to confirm dropping the Amazon keyspace: ").strip()
    if confirm == "YES":
        session.execute("DROP KEYSPACE IF EXISTS Amazon;")
        print("Amazon keyspace has been dropped.")
    else:
        print("Cancelled; keyspace was not dropped.")


def print_menu():
    print("\n===== Amazon Cassandra Menu =====")
    print("1. Display all distinct product categories")
    print("2. Count 4-star and higher reviews for a category")
    print("3. Count 1-star reviews for a category")
    print("4. Run a custom CQL SELECT statement")
    print("5. Add/remove a column from a table")
    print("6. Delete the Reviews and ProductCategories tables")
    print("7. Delete the Amazon keyspace")
    print("8. Exit")


def main():
    create_keyspace_and_tables()
    import_dataset()
    while True:
        print_menu()
        choice = input("Select an option (1-8): ").strip()
        if choice == "1":
            show_distinct_categories()
        elif choice == "2":
            count_high_star_reviews()
        elif choice == "3":
            count_one_star_reviews()
        elif choice == "4":
            run_custom_select()
        elif choice == "5":
            alter_columns()
        elif choice == "6":
            delete_tables()
        elif choice == "7":
            delete_keyspace()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid selection, please choose 1-8.")


if __name__ == "__main__":
    main()
