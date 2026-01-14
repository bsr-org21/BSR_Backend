from . import db

site_employee = db.Table(
    'site_employee',
    db.Column('site_id', db.Integer, db.ForeignKey('construction_sites.id'), primary_key=True),
    db.Column('employee_id', db.Integer, db.ForeignKey('employees.id'), primary_key=True)
)
    