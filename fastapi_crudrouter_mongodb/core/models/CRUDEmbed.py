class CRUDEmbed:
    def __init__(self, model, embed_name, identifier_field: str = "_id") -> None:
        self.model = model
        self.embed_name = embed_name
        self.identifier_field = identifier_field
