from app import db
from sqlalchemy import UniqueConstraint


# This class will hold all files owned by the user
# If the user is not logged in, he will not be able to save his work.
class Files(db.Model):
    __tablename__ = "files"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer)
    file_name    = db.Column(db.String)
    file_content = db.Column(db.String)
    tags         = db.Column(db.String)
    __table_args__ = (UniqueConstraint('user_id', 'file_name', name='unique_user_file'),)

    def __init__(self, user_id, file_name, file_content, tags):
        self.user_id      =  user_id
        self.file_name    = file_name
        self.file_content = file_content
        self.tags         = tags

    def serialize(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'file_name': self.file_name,
                'file_content': self.file_content,
                'tags': self.tags
            }
