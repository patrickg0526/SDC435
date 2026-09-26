#####################################################################
# Name: Patrick Gonzalez
# Date: 09/30/2026
# Assignment: 5.6 Performance Assessment - Python Application
#             Accessing a Relational Database
# Purpose: Menu-driven Python application that connects to a local
#          SQLite database named EN_ReviewData, creates Reviewers,
#          Categories, Products, and Reviews tables with referential
#          integrity, imports the review dataset, and lets the user
#          display categories with a minimum product count, run
#          custom SQL SELECT statements, insert rows, delete reviews
#          by category, and drop all tables.
#####################################################################

import sqlite3
import json

# *Configure the database connection
print("Connecting to local SQLite database...")
db = sqlite3.connect('EN_ReviewData.db')

DATASET_FILE = 'dataset_en_dev.json'
IMPORT_LIMIT = 2000  # Only import a sample; the full dataset is 5000 rows.


def create_tables():
    # *Create a new table named Reviewers with reviewer_id as the Primary Key
    db.execute('''
        CREATE TABLE IF NOT EXISTS Reviewers (
        reviewer_id TEXT PRIMARY KEY
        );
        ''')

    # *Create a new table named Categories with product_category as the Primary Key
    db.execute('''
        CREATE TABLE IF NOT EXISTS Categories (
        product_category TEXT PRIMARY KEY
        );
        ''')

    # *Create a new table named Products with product_id as the Primary Key and
    # product_category as a Foreign Key to the Categories table
    db.execute('''
        CREATE TABLE IF NOT EXISTS Products (
        product_id TEXT PRIMARY KEY,
        product_category TEXT,
        FOREIGN KEY(product_category) REFERENCES Categories(product_category)
        );
        ''')

    # *Create a new table named Reviews with review_id as the Primary Key,
    # product_id and reviewer_id as Foreign Keys to the Products and Reviewers tables
    db.execute('''
        CREATE TABLE IF NOT EXISTS Reviews (
        review_id TEXT PRIMARY KEY,
        product_id TEXT,
        reviewer_id TEXT,
        stars INTEGER,
        review_body TEXT,
        review_title TEXT,
        FOREIGN KEY(product_id) REFERENCES Products(product_id),
        FOREIGN KEY(reviewer_id) REFERENCES Reviewers(reviewer_id)
        );
        ''')
    db.commit()


def import_dataset(path=DATASET_FILE, limit=IMPORT_LIMIT):
    # *Insert data from the JSON file into the Reviewers, Categories, Products, and Reviews tables
    print(f"Importing up to {limit} reviews from file...")
    count = 0
    with open(path, 'r') as f:
        for line in f:
            if count >= limit:
                break
            data = json.loads(line)
            db.execute(
                "INSERT OR IGNORE INTO Reviewers (reviewer_id) VALUES (?);",
                [data["reviewer_id"]],
            )
            db.execute(
                "INSERT OR IGNORE INTO Categories (product_category) VALUES (?);",
                [data["product_category"]],
            )
            db.execute(
                "INSERT OR IGNORE INTO Products (product_id, product_category) VALUES (?, ?);",
                [data["product_id"], data["product_category"]],
            )
            db.execute(
                "INSERT OR IGNORE INTO Reviews (review_id, product_id, reviewer_id, stars, "
                "review_body, review_title) VALUES (?, ?, ?, ?, ?, ?);",
                [data["review_id"], data["product_id"], data["reviewer_id"],
                 int(data["stars"]), data["review_body"], data["review_title"]],
            )
            count += 1
    db.commit()
    print(f"Imported {count} review(s) into EN_ReviewData.\n")


def show_categories_with_min_products():
    # *Display the categories that have at least a certain number of products
    # determined by a user-entered value
    minimum = input("Show categories with at least how many products? ").strip()
    minimum = int(minimum) if minimum.isdigit() else 0
    query = '''
        SELECT product_category, COUNT(product_id) FROM Products
        GROUP BY product_category
        HAVING COUNT(product_id) >= ?;
        '''
    result = db.execute(query, [minimum])
    rows = result.fetchall()
    if not rows:
        print(f"No categories have {minimum} or more products.")
        return
    print(f"\nCategories with at least {minimum} product(s):")
    for row in rows:
        print(row)


def run_custom_select():
    # *Allow the user to type in and execute SQL SELECT statements
    query = input("Enter a SQL SELECT statement (without trailing semicolon): ").strip()
    if not query.lower().startswith("select"):
        print("Only SELECT statements are allowed here.")
        return
    try:
        result = db.execute(query + ";" if not query.endswith(";") else query)
        count = 0
        for row in result:
            print(row)
            count += 1
            if count >= 25:
                print("... (showing first 25 rows)")
                break
        if count == 0:
            print("No rows returned.")
    except sqlite3.Error as e:
        print(f"Error running query: {e}")


def insert_row():
    # *Allow the user to insert a row into any table
    table = input("Which table? (Reviewers/Categories/Products/Reviews): ").strip()
    if table == "Reviewers":
        reviewer_id = input("reviewer_id: ").strip()
        db.execute("INSERT INTO Reviewers (reviewer_id) VALUES (?);", [reviewer_id])
    elif table == "Categories":
        category = input("product_category: ").strip()
        db.execute("INSERT INTO Categories (product_category) VALUES (?);", [category])
    elif table == "Products":
        product_id = input("product_id: ").strip()
        category = input("product_category: ").strip()
        db.execute(
            "INSERT INTO Products (product_id, product_category) VALUES (?, ?);",
            [product_id, category],
        )
    elif table == "Reviews":
        review_id = input("review_id: ").strip()
        product_id = input("product_id: ").strip()
        reviewer_id = input("reviewer_id: ").strip()
        stars = input("stars: ").strip()
        body = input("review_body: ").strip()
        title = input("review_title: ").strip()
        db.execute(
            "INSERT INTO Reviews (review_id, product_id, reviewer_id, stars, review_body, review_title) "
            "VALUES (?, ?, ?, ?, ?, ?);",
            [review_id, product_id, reviewer_id, int(stars) if stars.isdigit() else 0, body, title],
        )
    else:
        print("Please enter Reviewers, Categories, Products, or Reviews.")
        return
    db.commit()
    print(f"Row inserted into {table}.")


def delete_reviews_by_category():
    # *Delete all records in the Reviews table for a user-entered product_category
    category = input("Delete all reviews for which product_category? ").strip()
    query = '''
        DELETE FROM Reviews WHERE product_id IN (
            SELECT product_id FROM Products WHERE product_category = ?
        );
        '''
    cursor = db.execute(query, [category])
    db.commit()
    print(f"Deleted {cursor.rowcount} review(s) for category '{category}'.")


def delete_all_tables():
    # *Allow the user to delete all tables in the database
    confirm = input("Type YES to confirm dropping all tables: ").strip()
    if confirm != "YES":
        print("Cancelled; tables were not dropped.")
        return
    db.execute("DROP TABLE IF EXISTS Reviews;")
    db.execute("DROP TABLE IF EXISTS Products;")
    db.execute("DROP TABLE IF EXISTS Categories;")
    db.execute("DROP TABLE IF EXISTS Reviewers;")
    db.commit()
    print("All tables have been dropped.")


def print_menu():
    print("\n===== EN_ReviewData Menu =====")
    print("1. Display categories with a minimum product count")
    print("2. Run a custom SQL SELECT statement")
    print("3. Insert a row into a table")
    print("4. Delete all reviews for a category")
    print("5. Delete all tables")
    print("6. Exit")


def main():
    create_tables()
    import_dataset()
    while True:
        print_menu()
        choice = input("Select an option (1-6): ").strip()
        if choice == "1":
            show_categories_with_min_products()
        elif choice == "2":
            run_custom_select()
        elif choice == "3":
            insert_row()
        elif choice == "4":
            delete_reviews_by_category()
        elif choice == "5":
            delete_all_tables()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid selection, please choose 1-6.")
    db.close()


if __name__ == "__main__":
    main()
