from . import db
from datetime import date

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'present', 'absent', 'half'

    # Ensure one record per employee per day
    __table_args__ = (db.UniqueConstraint('employee_id', 'date', name='_emp_date_uc'),)
