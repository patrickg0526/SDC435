#####################################################################
# Name: Patrick Gonzalez
# Date: 09/10/2026
# Assignment: 2.5 Performance Assessment - Python Application
#             Accessing a Document Database
# Purpose: Menu-driven Python application that connects to a local
#          MongoDB "Amazon" database / "ReviewData" collection,
#          imports the review dataset, and lets the user create,
#          read (with advanced filters), update, and delete review
#          documents interactively.
#####################################################################

import json
import pymongo

# *Configure the database connection
print("Connecting to local Mongo database...")
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Amazon"]
collection = db["ReviewData"]


def import_dataset(path='dataset_amazon.json'):
    # *Import the JSON dataset into the ReviewData collection
    print("Importing data from file...")
    count = 0
    with open(path, 'r') as f:
        for line in f:
            data = json.loads(line)
            collection.insert_one(data)
            count += 1
    print(f"Imported {count} review document(s) into Amazon.ReviewData.\n")


def create_review():
    # *Create a new document in the ReviewData collection
    print("\nEnter the new review's details:")
    review = {
        "review_id": input("  review_id: ").strip(),
        "product_id": input("  product_id: ").strip(),
        "reviewer_id": input("  reviewer_id: ").strip(),
        "stars": input("  stars: ").strip(),
        "review_body": input("  review_body: ").strip(),
        "review_title": input("  review_title: ").strip(),
        "language": input("  language: ").strip(),
        "product_category": input("  product_category: ").strip(),
    }
    result = collection.insert_one(review)
    print(f"Inserted new review with _id: {result.inserted_id}")


def find_one_review():
    # *Retrieve a document using the find_one function
    review_id = input("Enter a review_id to look up (blank for any document): ").strip()
    query = {"review_id": review_id} if review_id else {}
    doc = collection.find_one(query)
    if doc:
        print(doc)
    else:
        print("No matching document found.")


def find_stars_gte():
    # *Filter using find() for stars >= a user-entered number
    stars = input("Show reviews with stars greater than or equal to: ").strip()
    query = {"stars": {"$gte": stars}}
    results = list(collection.find(query).limit(10))
    print(f"Found {len(results)} matching document(s) (showing up to 10):")
    for doc in results:
        print(doc)


def find_stars_lt():
    # *Filter using find() for stars < a user-entered number
    stars = input("Show reviews with stars less than: ").strip()
    query = {"stars": {"$lt": stars}}
    results = list(collection.find(query).limit(10))
    print(f"Found {len(results)} matching document(s) (showing up to 10):")
    for doc in results:
        print(doc)


def find_word_in_title():
    # *Filter using find() for a user-entered word within review_title
    word = input("Show reviews with this word in the title: ").strip()
    query = {"review_title": {"$regex": word, "$options": "i"}}
    results = list(collection.find(query).limit(10))
    print(f"Found {len(results)} matching document(s) (showing up to 10):")
    for doc in results:
        print(doc)


def find_word_in_body():
    # *Filter using find() for a user-entered word within review_body
    word = input("Show reviews with this word in the body: ").strip()
    query = {"review_body": {"$regex": word, "$options": "i"}}
    results = list(collection.find(query).limit(10))
    print(f"Found {len(results)} matching document(s) (showing up to 10):")
    for doc in results:
        print(doc)


def update_review():
    # *Allow the user to enter a field and update its value
    review_id = input("Enter the review_id of the document to update: ").strip()
    field = input("Enter the field name to update: ").strip()
    value = input("Enter the new value: ").strip()
    result = collection.update_one({"review_id": review_id}, {"$set": {field: value}})
    if result.matched_count:
        print(f"Updated '{field}' on review '{review_id}'.")
    else:
        print(f"No document found with review_id '{review_id}'.")


def delete_review():
    # *Allow the user to enter a document ID and delete that document
    doc_id = input("Enter the _id of the document to delete: ").strip()
    try:
        from bson.objectid import ObjectId
        result = collection.delete_one({"_id": ObjectId(doc_id)})
    except Exception:
        result = collection.delete_one({"_id": doc_id})
    if result.deleted_count:
        print(f"Deleted document with _id '{doc_id}'.")
    else:
        print(f"No document found with _id '{doc_id}'.")


def delete_all_documents():
    # *Menu option to remove all documents in the collection
    confirm = input("Type YES to confirm deleting ALL documents in ReviewData: ").strip()
    if confirm == "YES":
        result = collection.delete_many({})
        print(f"Deleted {result.deleted_count} document(s). Collection is now empty.")
    else:
        print("Cancelled; no documents were removed.")


def delete_collection():
    # *Menu option to delete the ReviewData collection from the Amazon database
    confirm = input("Type YES to confirm dropping the ReviewData collection: ").strip()
    if confirm == "YES":
        collection.drop()
        print("ReviewData collection has been dropped.")
    else:
        print("Cancelled; collection was not dropped.")


def print_menu():
    print("\n===== Amazon.ReviewData Menu =====")
    print("1. Create a new review")
    print("2. Find a review with find_one()")
    print("3. Find reviews with stars >= a number")
    print("4. Find reviews with stars < a number")
    print("5. Find reviews with a word in the title")
    print("6. Find reviews with a word in the body")
    print("7. Update a field on a review")
    print("8. Delete a review by _id")
    print("9. Delete ALL documents in the collection")
    print("10. Delete the ReviewData collection")
    print("11. Exit")


def main():
    import_dataset()
    while True:
        print_menu()
        choice = input("Select an option (1-11): ").strip()
        if choice == "1":
            create_review()
        elif choice == "2":
            find_one_review()
        elif choice == "3":
            find_stars_gte()
        elif choice == "4":
            find_stars_lt()
        elif choice == "5":
            find_word_in_title()
        elif choice == "6":
            find_word_in_body()
        elif choice == "7":
            update_review()
        elif choice == "8":
            delete_review()
        elif choice == "9":
            delete_all_documents()
        elif choice == "10":
            delete_collection()
        elif choice == "11":
            print("Goodbye!")
            break
        else:
            print("Invalid selection, please choose 1-11.")


if __name__ == "__main__":
    main()
