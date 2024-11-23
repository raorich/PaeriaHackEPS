from flask_sqlalchemy import SQLAlchemy
import datetime

# Inicializar SQLAlchemy
db = SQLAlchemy()

class TypeRegister(db.Model):
    __tablename__ = 'type_register'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f'<TypeRegister {self.name}>'
    
class DoorRegisters(db.Model):
    __tablename__ = 'door_registers'
    
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('type_register.id'), nullable=False)
    parking_id = db.Column(db.Integer, db.ForeignKey('parking.id'), nullable=False)
    #date_history = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # foreing keys
    #histories = db.relationship('History', backref='door_register', lazy=True)
    
    def __repr__(self):
        return f'<DoorRegisters {self.id}>'

class Ticket(db.Model):
    __tablename__ = 'ticket'
    
    id = db.Column(db.Integer, primary_key=True)
    ubication = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, default=True)
    
    # foreing keys
    #histories = db.relationship('History', backref='ticket', lazy=True)
    parking_id = db.Column(db.Integer, db.ForeignKey('parking.id'), nullable=False)
    
    def __repr__(self):
        return f'<Ticket {self.id}>'

class History(db.Model):
    __tablename__ = 'history'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # foreing keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    door_register_id = db.Column(db.Integer, db.ForeignKey('door_registers.id'), nullable=False)
    parking_id = db.Column(db.Integer, db.ForeignKey('parking.id'), nullable=False) 
    
    def __repr__(self):
        return f'<History {self.id}>'
    
class Parking(db.Model):
    __tablename__ = 'parking'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(300), nullable=False)
    total_capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    
    #histories = db.Column(db.Integer, db.ForeignKey('history.id'), nullable=False)
    histories = db.relationship('History', backref='parking', lazy=True) 
    controllers = db.relationship('Controller', backref='parking', lazy=True) 
    
    def __repr__(self):
        return f'<Parking {self.name}>'
    
class Controller(db.Model):
    __tablename__ = 'controller'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    mac = db.Column(db.String(100), nullable=False)

    parking_id = db.Column(db.Integer, db.ForeignKey('parking.id'), nullable=False) 

    def __repr__(self):
        return f'<Controller {self.name}>'
    
