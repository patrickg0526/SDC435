#####################################################################
# Name: Patrick Gonzalez
# Date: 09/06/2026
# Assignment: 1.8 Performance Assessment - Python Application Accessing
#             a Key-Value Database
# Purpose: Menu-driven CRUD application for a Redis key-value database.
#          Imports a review dataset into Redis as sets, then lets the
#          user create, read, update, and delete sets interactively.
#####################################################################

import json
import redis

r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0, decode_responses=True)


def import_dataset(path='dataset_en_dev.json'):
    # *Configure the database connection and import the dataset
    print("Connecting to local Redis database...")
    count = 0
    with open(path, 'r') as f:
        for line in f:
            data = json.loads(line)
            key = "ReviewID:" + data["review_id"] + ":ReviewerID:" + \
                data["reviewer_id"] + ":ProductID:" + data["product_id"]
            r.sadd(key, "Stars:" + data["stars"])
            r.sadd(key, "ReviewBody:" + data["review_body"])
            r.sadd(key, "ReviewTitle:" + data["review_title"])
            r.sadd(key, "Language:" + data["language"])
            r.sadd(key, "ProductCategory:" + data["product_category"])
            count += 1
    print(f"Imported {count} review set(s) into Redis.")


def create_set():
    # *Create a new set in the Redis database
    key = input("Enter a name for the new set: ").strip()
    raw = input("Enter one or more members, separated by commas: ").strip()
    members = [m.strip() for m in raw.split(",") if m.strip()]
    if not members:
        print("No members entered; nothing created.")
        return
    added = r.sadd(key, *members)
    print(f"Created set '{key}' - {added} member(s) added.")


def read_set():
    # *Retrieve the members of a specific set from the Redis database
    key = input("Enter the set name to view: ").strip()
    if not r.exists(key):
        print(f"Set '{key}' does not exist.")
        return
    members = r.smembers(key)
    print(f"Members of '{key}' ({len(members)} total):")
    for m in members:
        print(" -", m)


def update_set():
    # *Update the members of a specific set in the Redis database
    key = input("Enter the set name to update: ").strip()
    if not r.exists(key):
        print(f"Set '{key}' does not exist.")
        return
    action = input("Type 'add' to add members or 'remove' to remove members: ").strip().lower()
    raw = input("Enter one or more members, separated by commas: ").strip()
    members = [m.strip() for m in raw.split(",") if m.strip()]
    if not members:
        print("No members entered; nothing changed.")
        return
    if action == "add":
        changed = r.sadd(key, *members)
        print(f"Added {changed} member(s) to '{key}'.")
    elif action == "remove":
        changed = r.srem(key, *members)
        print(f"Removed {changed} member(s) from '{key}'.")
    else:
        print("Unrecognized action; nothing changed.")


def delete_set():
    # *Delete a specific set from the Redis database
    key = input("Enter the set name to delete: ").strip()
    deleted = r.delete(key)
    if deleted:
        print(f"Set '{key}' deleted.")
    else:
        print(f"Set '{key}' did not exist.")


def delete_all():
    # *Delete all data from the Redis database
    confirm = input("Type YES to confirm deleting ALL data in the database: ").strip()
    if confirm == "YES":
        r.flushdb()
        print("All data removed from the database.")
    else:
        print("Cancelled; no data was removed.")


def print_menu():
    print("\n===== Redis Key-Value Database Menu =====")
    print("1. Create a new set")
    print("2. Read (view) a set")
    print("3. Update a set (add/remove members)")
    print("4. Delete a set")
    print("5. Delete ALL data from the database")
    print("6. Exit")


def main():
    import_dataset()
    while True:
        print_menu()
        choice = input("Select an option (1-6): ").strip()
        if choice == "1":
            create_set()
        elif choice == "2":
            read_set()
        elif choice == "3":
            update_set()
        elif choice == "4":
            delete_set()
        elif choice == "5":
            delete_all()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid selection, please choose 1-6.")


if __name__ == "__main__":
    main()
