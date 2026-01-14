from . import db
from .site_employee import site_employee

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    name_tamil = db.Column(db.Unicode(100), nullable=True) # Added missing column
    gender = db.Column(db.String(10), nullable=True)
        
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=True)
    
    attendances = db.relationship('Attendance', backref='employee', lazy=True)
    position = db.relationship('Position', backref='employees')

    construction_sites = db.relationship(
        'ConstructionSite',
        secondary=site_employee,
        back_populates='employees'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_tamil': self.name_tamil,
            'position': self.position.title if self.position else None,
            'position_tamil': self.position.title_tamil if self.position else None,
            'site_ids': [site.id for site in self.construction_sites]
        }