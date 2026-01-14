from . import db
from datetime import datetime
from .site_employee import site_employee

class ConstructionSite(db.Model):
    __tablename__ = 'construction_sites'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)

    name_tamil = db.Column(db.Unicode(100), nullable=True)
    owner_name_tamil = db.Column(db.Unicode(100), nullable=True)
    location_tamil = db.Column(db.Unicode(200), nullable=True)

    employees = db.relationship(
        'Employee',
        secondary=site_employee,
        back_populates='construction_sites'
    )
    
    def to_dict(self):
        start_date = self.start_date
        if isinstance(start_date, str):
            if start_date == '0000-00-00':
                start_date = None  
            else:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = self.end_date
        if end_date and isinstance(end_date, str):
            if end_date == '0000-00-00':
                end_date = None
            else:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        return {
            'id': self.id,
            'name': self.name,
            'owner_name': self.owner_name,
            'location': self.location,
            'name_tamil': self.name_tamil,
            'owner_name_tamil': self.owner_name_tamil,
            'location_tamil': self.location_tamil,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None
        }