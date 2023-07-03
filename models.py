class Pessoa:
    def __init__(self, nome, carteira_id, lista):
        self.nome = nome
        self.carteira_id = carteira_id
        self.lista = lista

class Objekt:
    def __init__(self, collectionId, season, member, collectionNo, class_type, transferable, owner):
        self.collectionId = collectionId
        self.season = season
        self.member = member
        self.collectionNo = collectionNo
        self.class_type = class_type
        self.transferable = transferable
        self.owner = owner