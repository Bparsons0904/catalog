Catalog Project README

Configuration Instruction
1. Requires a working vagrant environment, including Python, Flask and sqlalchemy installations.

Installation Instruction
1. Place contents of catalog along with static and template folders in vagrant folder.

Operating Instruction
1. Create database by running database_setup.py.
1. Start project by running catalog.py.
2. Without logging in, can view available categories, item list, item details and featured items,
3. Use Google Login to add ability to add, delete and modify items.

Available Public Endpoints from http://localhost:8000/
1. Home Page, list of available Categories and Featured Items / and /catalog
2. Items Listing /catalog/"catalog_name" and /catalog/"catalog_name"/item
3. Item Details c & /catalog/"catalog_name"/item/item_id
4. Login screen at /login
5. JSON available for all listed endpoints

Additional Private Endpoints from http://localhost:8000/
1. Add Item available at /catalog/"catalog_name"/item/add
2. Delete Item available at /catalog/"catalog_name"/item_id/delete
3. Edit Item available at /catalog/"catalog_name"/item_id/Edit
4. Logout available at /disconnect
