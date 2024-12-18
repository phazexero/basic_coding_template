# db/queries/queries.py
GET_ITEM_QUERY = """
    select * from ledgers where organization_id = :item_id
"""
