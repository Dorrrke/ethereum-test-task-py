from app import db, session, Base


class Proposal(Base):
    __tablename__ = 'Proposals'
    pid = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    def __init__(self,header, description):
        self.header = header
        self.description = description
    
    def __str__(self) -> str:
        return f"{self.header} and {self.description}"
    
    # def __dict__(self):
    #     return {"header": self.header, "description":self.description}

    

class Vote(Base):
    __tablename__ = 'Votes'
    vid = db.Column(db.Integer, primary_key=True)
    vote = db.Column(db.Boolean, nullable=False)
    userBalance = db.Column(db.String(250), nullable=False)
    blockNumber = db.Column(db.String(250), nullable=False)
    pid = db.Column(db.Integer, nullable=False)
    def __init__(self, vote):
        self.vote = vote


class User(Base):
    __tablename__ = 'Users'
    uid = db.Column(db.Integer, primary_key=True)
    addr = db.Column(db.String(250), nullable=False)
    blockNumber = db.Column(db.String, nullable=False)
    isAdmin = db.Column(db.Boolean, nullable=False)
    def __init__(self, addr, blockNumber, isAdmin):
        self.addr = addr
        self.blockNumber = blockNumber
        self.isAdmin = isAdmin