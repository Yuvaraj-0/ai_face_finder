from models.token_blacklist import TokenBlacklist

class BlacklistService:

    def add(self, db, token):
        db.add(TokenBlacklist(token=token))
        db.commit()

    def is_blacklisted(self, db, token):
        return db.query(TokenBlacklist).filter_by(token=token).first() is not None