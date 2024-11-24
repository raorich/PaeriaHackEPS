import random
from datetime import datetime, timedelta
import main

# Configuración inicial
PARKING_ID = 5  # Parking PK0005
ENTRADA = 1
SALIDA = 2

# Parámetros de generación
NUM_REGISTROS = 200  # Número total de registros de DoorRegisters/History * 2


with main.app.app_context():
    tickets = main.Ticket.query.filter_by(parking_id=PARKING_ID).all()

    # Crear DoorRegisters y History aleatorios
    for _ in range(NUM_REGISTROS):
        ticket = random.choice(tickets)
        tipo = ENTRADA
        
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 12, 31)
        random_date = start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))
        
        # Crear registro de DoorRegister
        door_register = main.DoorRegisters(type_id=tipo, parking_id=PARKING_ID)
        main.db.session.add(door_register)
        main.db.session.commit()  # Necesario para obtener el ID
        
        # Crear registro de History vinculado
        history = main.History(
            date=random_date,
            ticket_id=ticket.id,
            door_register_id=door_register.id,
            parking_id=PARKING_ID
        )
        main.db.session.add(history)

        print(f"Entrada: {history.id}")

        # Asegurar que salidas sean posteriores a entradas
        if tipo == ENTRADA:
            salida_date = random_date + timedelta(minutes=random.randint(10, 300))  # Salida entre 10 minutos y 5 horas después
            salida_register = main.DoorRegisters(type_id=SALIDA, parking_id=PARKING_ID)
            main.db.session.add(salida_register)
            main.db.session.commit()

            salida_history = main.History(
                date=salida_date,
                ticket_id=ticket.id,
                door_register_id=salida_register.id,
                parking_id=PARKING_ID
            )
            main.db.session.add(salida_history)
            print(f"Salida: {salida_history.id}")
        
        

    # Confirmar transacciones
    main.db.session.commit()

print("Registros generados con éxito.")