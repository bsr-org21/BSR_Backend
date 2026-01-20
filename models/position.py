from . import db

class Position(db.Model):
    __tablename__ = 'positions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    title_tamil = db.Column(db.Unicode(100), nullable=True)
    salary = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'title_tamil': self.title_tamil,
            'salary': self.salary
        }