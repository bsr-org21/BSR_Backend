from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from sqlalchemy import inspect
from models import db
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300
}

db.init_app(app)

from models.construction_site import ConstructionSite
from models.employee import Employee
from models.position import Position
from models.attendance import Attendance

with app.app_context():
    db.create_all()
    # Add missing columns if they don't exist
    inspector = inspect(db.engine)
    
    # Get and print all table names
    table_names = inspector.get_table_names()
    print("Tables in database:", table_names)

def parse_date(value):
    if not value or value in ("null", "None"):
        return None

    # Accept both full datetime & date-only
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Invalid date format: {value}")

@app.route('/construction_sites', methods=['GET'])
def get_construction_sites():
    sites = ConstructionSite.query.all()
    return jsonify([site.to_dict() for site in sites]), 200

@app.route('/construction_sites', methods=['POST'])
def add_construction_site():
    data = request.get_json()

    site = ConstructionSite(
        name=data['name'],
        owner_name=data['owner_name'],
        location=data['location'],
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date')),
        name_tamil=data.get('name_tamil'),
        owner_name_tamil=data.get('owner_name_tamil'),
        location_tamil=data.get('location_tamil')
    )

    db.session.add(site)
    db.session.commit()
    return jsonify(site.to_dict()), 201

@app.route('/construction_sites', methods=['PUT'])
def update_construction_site():
    data = request.get_json()
    site = ConstructionSite.query.get_or_404(data['id'])  
    
    for key, value in data.items():
        if key == 'id':
            continue
        if key in ['start_date', 'end_date']:
            setattr(site, key, parse_date(value))
        else:
            setattr(site, key, value)

    db.session.commit()
    return jsonify({"message": "Construction site updated successfully"})

@app.route('/delete_site/<int:site_id>',methods=['DELETE'])
def delete_site(site_id):
    site = ConstructionSite.query.get_or_404(site_id)
    db.session.delete(site)
    db.session.commit()
    return jsonify({'message': 'Site deleted successfully'}), 200

@app.route('/employees',methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    return jsonify([emp.to_dict() for emp in employees]), 200

@app.route('/employees', methods=['POST'])
def add_employee():
    data = request.get_json()
    print(data)
    pos = Position.query.filter_by(title=data.get('position')).first()

    employee = Employee(
        name=data['name'],
        name_tamil=data.get('name_tamil'),
        gender=data.get('gender'),
        position=pos 
    )

    site_ids = data.get('site_ids')
    print(site_ids)
    if site_ids:
        for site_id in site_ids:
            site = ConstructionSite.query.get(site_id)
            if site:
                employee.construction_sites.append(site)

    db.session.add(employee)
    db.session.commit()
    
    return jsonify(employee.to_dict()), 201

@app.route('/employees', methods=['PUT'])
def update_employee():
    data = request.get_json()

    if not data or 'id' not in data:
        return jsonify({"error": "Employee ID is required"}), 400
        
    employee = Employee.query.get_or_404(data['id'])  

    allowed_keys = ['name', 'name_tamil', 'gender']
    for key in allowed_keys:
        if key in data:
            setattr(employee, key, data[key])

    if 'position' in data:
        pos = Position.query.filter_by(title=data['position']).first()
        employee.position = pos

    if 'site_ids' in data:
        new_site_list = ConstructionSite.query.filter(ConstructionSite.id.in_(data['site_ids'])).all()
        employee.construction_sites = new_site_list

    db.session.commit()
    return jsonify({"message": "Employee updated successfully"})

@app.route('/delete_employee/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': 'Employee deleted successfully'}), 200

@app.route('/positions', methods=['GET'])
def get_positions():    
    positions = Position.query.all()
    return jsonify([pos.to_dict() for pos in positions]), 200

@app.route('/positions', methods=['POST'])
def add_position():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
        
    new_pos = Position(
        title=data['title'],
        title_tamil=data.get('title_tamil')
    )
    db.session.add(new_pos)
    db.session.commit()
    return jsonify(new_pos.to_dict()), 201

@app.route('/positions/<int:pos_id>', methods=['PUT'])
def update_position(pos_id):
    data = request.get_json()
    pos = Position.query.get_or_404(pos_id)
    
    pos.title = data.get('title', pos.title)
    pos.title_tamil = data.get('title_tamil', pos.title_tamil)
    
    db.session.commit()
    return jsonify(pos.to_dict()), 200

@app.route('/positions/<int:pos_id>', methods=['DELETE'])
def delete_position(pos_id):
    pos = Position.query.get_or_404(pos_id)
    db.session.delete(pos)
    db.session.commit()
    return jsonify({'message': 'Position deleted successfully'}), 200

@app.route('/attendance', methods=['GET'])
def get_attendance():
    date_str = request.args.get('date') # Expects YYYY-MM-DD
    if not date_str:
        return jsonify({"error": "Date is required"}), 400
    
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    records = Attendance.query.filter_by(date=target_date).all()
    
    return jsonify({
        r.employee_id: r.status for r in records
    })

@app.route('/attendance', methods=['POST'])
def save_attendance():
    data = request.json  # Expecting a list of records
    date_str = data.get('date')
    records = data.get('records')

    if not date_str or not records:
        return jsonify({"error": "Missing data"}), 400

    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    for item in records:
        # Check if record already exists for this date/employee
        existing = Attendance.query.filter_by(
            employee_id=item['employee_id'], 
            date=target_date
        ).first()

        if existing:
            existing.status = item['status']
        else:
            new_record = Attendance(
                employee_id=item['employee_id'],
                date=target_date,
                status=item['status']
            )
            db.session.add(new_record)

    db.session.commit()
    return jsonify({"message": "Attendance saved successfully"}), 201

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
