import main
import logs
import numpy as np

def predict_parking_occupation():
    '''
        Eric això ha estat un infern tu explicare demà pero no modifiquis res del codi perque mareta
    '''
    # Parse input data
    data = main.request.get_json()
    parking_id = data.get("parking_id")

    # Validate input
    if not parking_id:
        return main.jsonify({"error": "parking_id is required"}), 400

    # Query historical data for the given parking ID
    history_data = main.History.query.filter_by(parking_id=parking_id).all()

    # If no historical data is found, return an empty response
    if not history_data:
        return main.jsonify([])

    # Convert query results to a DataFrame
    df = main.pd.DataFrame([{
        "date": record.date,
        "ticket_id": record.ticket_id,
        "door_register_id": record.door_register_id
    } for record in history_data])

    if df.empty:
        return main.jsonify({"error": "No data available for this parking."}), 404
    
    parking = main.Parking.query.filter_by(id=parking_id).first()
    if not parking or parking.total_capacity == 0:
        return main.jsonify({"error": "Invalid parking capacity."}), 400

    total_capacity = parking.total_capacity

    door_registers = main.DoorRegisters.query.filter(
        main.DoorRegisters.parking_id == parking_id,
        main.DoorRegisters.id.in_(df['door_register_id'])
    ).with_entities(
        main.DoorRegisters.id.label('door_register_id'),
        main.DoorRegisters.type_id.label('type_id')
    ).all()

    door_registers_df = main.pd.DataFrame([{
        "door_register_id": record.door_register_id,
        "type_id": record.type_id
    } for record in door_registers])

    df = df.merge(door_registers_df, on="door_register_id")
    door_types = {1: "entry", 2: "exit"}
    df["type"] = df["type_id"].map(door_types)

    # Sort by date to maintain logical order of events
    df = df.sort_values("date")

    # Pair entries and exits manually
    #trobar aquet fall ha estat una locura
    tickets = []
    active_tickets = {}

    for _, row in df.iterrows():
        ticket_id = row["ticket_id"]
        door_register_id = row["door_register_id"]
        date = row["date"]
        type_ = row["type"]

        if type_ == "entry":
            # Afegim l'entrada al diccionari només si no existeix ja
            if ticket_id not in active_tickets:
                active_tickets[ticket_id] = {"entry_time": date, "door_register_id": door_register_id}
            else:
                # Comprova si aquest door_register_id és més baix que l'existent
                if door_register_id < active_tickets[ticket_id]["door_register_id"]:
                    active_tickets[ticket_id] = {"entry_time": date, "door_register_id": door_register_id}

        elif type_ == "exit":
            # Si trobem una sortida per un ticket actiu, creem un registre complet
            if ticket_id in active_tickets:
                entry_data = active_tickets.pop(ticket_id)  # Traiem l'entrada per a aquest ticket
                tickets.append({
                    "entry_time": entry_data["entry_time"],
                    "exit_time": date
                })

    tickets_df = main.pd.DataFrame(tickets)
    print(tickets_df)

    # Align periods to full hours
    tickets_df["entry_time"] = tickets_df["entry_time"].dt.floor("h")
    tickets_df["exit_time"] = tickets_df["exit_time"].dt.ceil("h")

    # Generate periods occupied
    occupied_periods = []
    for _, row in tickets_df.iterrows():
        periods = main.pd.date_range(start=row["entry_time"], end=row["exit_time"], freq="h").tolist()
        for period in periods:
            occupied_periods.append({"timestamp": period})

    # Create DataFrame of occupied periods
    periods_df = main.pd.DataFrame(occupied_periods)

    # Count the number of tickets active per hour
    hourly_df = periods_df.groupby("timestamp").size().reset_index(name="tickets_active")
    november_hourly = hourly_df[hourly_df["timestamp"].dt.month == 11]
    # Mostrar les dades filtrades
    print("Dades de novembre (hourly_df):")
    print(november_hourly.to_string(index=False))

    # Align timestamps to hour intervals
    hourly_df["timestamp"] = hourly_df["timestamp"].dt.floor("h")

    # Create final DataFrame
    result_df = hourly_df.rename(columns={"timestamp": "period_start"})
    result_df["period_end"] = result_df["period_start"] + main.datetime.timedelta(hours=1)

    # Add additional time-related columns
    result_df["day_of_week"] = result_df["period_start"].dt.weekday
    result_df["hour"] = result_df["period_start"].dt.hour
    result_df["month"] = result_df["period_start"].dt.month
    result_df["occupation_ratio"] = result_df["tickets_active"] / total_capacity
   
    if result_df.empty:
        return main.jsonify({"error": "No data available for the given period."}), 404

    # Generate a complete table with all day_of_week, hour, and month combinations
    full_range = main.pd.date_range(start=result_df["period_start"].min(), 
                                    end=result_df["period_start"].max(), 
                                    freq="h")
    full_timeline = main.pd.DataFrame({
        "period_start": full_range,
        "day_of_week": full_range.weekday,
        "hour": full_range.hour,
        "month": full_range.month
    })

    if full_timeline.empty:
        return main.jsonify({"error": "Timeline generation failed."}), 404

    # Merge result_df into the complete timeline, filling missing values with 0
    complete_df = full_timeline.merge(result_df, on=["period_start", "day_of_week", "hour", "month"], how="left")
    complete_df["tickets_active"] = complete_df["tickets_active"].fillna(0)
    complete_df["occupation_ratio"] = complete_df["occupation_ratio"].fillna(0)

    # Calculate average occupation by day_of_week, hour, and month
    summary_df = complete_df.groupby(["month", "day_of_week", "hour"]).agg({
        "occupation_ratio": "mean"
    }).reset_index()

    summary_df = summary_df.rename(columns={"occupation_ratio": "predicted_occupation_probability"})
    if summary_df.empty:
        return main.jsonify({"error": "Summary generation failed."}), 404

    # Predict next 3 days based on current day and month
    current_date = main.datetime.datetime.now()
    #force date to test
    #current_date = main.datetime.datetime(2023, 5, 30) 

    predictions = []

    for i in range(3):  # Predict for the next 3 days
        target_date = current_date + main.datetime.timedelta(days=i)
        target_day = target_date.weekday()
        target_month = target_date.month

        # Generate 3-hour intervals
        for start_hour in range(0, 24, 3):
            end_hour = start_hour + 3

            # Filter historical data for the specific day, month, and hour interval
            interval_rows = summary_df[
                (summary_df["month"] == target_month) &
                (summary_df["day_of_week"] == target_day) &
                (summary_df["hour"] >= start_hour) &
                (summary_df["hour"] < end_hour)
            ]

            print(interval_rows)

            # Calculate mean or fallback to 0
            predicted_probability = (
                interval_rows["predicted_occupation_probability"].mean()
                if not interval_rows.empty
                else 0
            )
            print(predicted_probability)

            predictions.append({
                "day": target_date.strftime("%Y-%m-%d"),
                "hour": f"{start_hour:02d}:00-{end_hour:02d}:00",
                "predicted_occupation_probability": round(predicted_probability, 2)
            })

    return main.jsonify(predictions)



def predict_parking_occupation_old():
    '''
        Eric això ha estat un infern tu explicare demà pero no modifiquis res del codi perque mareta
    '''
    # Parse input data
    data = main.request.get_json()
    parking_id = data.get("parking_id")

    # Validate input
    if not parking_id:
        return main.jsonify({"error": "parking_id is required"}), 400

    # Query historical data for the given parking ID
    history_data = main.History.query.filter_by(parking_id=parking_id).all()

    # If no historical data is found, return an empty response
    if not history_data:
        return main.jsonify([])

    # Convert query results to a DataFrame
    df = main.pd.DataFrame([{
        "date": record.date,
        "ticket_id": record.ticket_id,
        "door_register_id": record.door_register_id
    } for record in history_data])

    if df.empty:
        return main.jsonify({"error": "No data available for this parking."}), 404
    
    parking = main.Parking.query.filter_by(id=parking_id).first()
    if not parking or parking.total_capacity == 0:
        return main.jsonify({"error": "Invalid parking capacity."}), 400

    total_capacity = parking.total_capacity

    # Fetch door registers and add type information (entry/exit)
    door_registers = main.DoorRegisters.query.filter(
        main.DoorRegisters.id.in_(df['door_register_id'])
    ).with_entities(
        main.DoorRegisters.id.label('door_register_id'),
        main.DoorRegisters.type_id.label('type_id')
    ).all()

    door_registers_df = main.pd.DataFrame([{
        "door_register_id": record.door_register_id,
        "type_id": record.type_id
    } for record in door_registers])

    df = df.merge(door_registers_df, on="door_register_id")
    door_types = {1: "entry", 2: "exit"}
    df["type"] = df["type_id"].map(door_types)

    # Sort by date to maintain logical order of events
    df = df.sort_values("date")

    # Pair entries and exits manually
    tickets = []
    for ticket_id, group in df.groupby("ticket_id"):
        entry = group[group["type"] == "entry"]["date"].min()
        exit_ = group[group["type"] == "exit"]["date"].max()
        if entry and exit_:
            tickets.append({"entry_time": entry, "exit_time": exit_})

    tickets_df = main.pd.DataFrame(tickets)

    # Align periods to full hours
    tickets_df["entry_time"] = tickets_df["entry_time"].dt.floor("h")
    tickets_df["exit_time"] = tickets_df["exit_time"].dt.ceil("h")

    # Generate periods occupied
    occupied_periods = []
    for _, row in tickets_df.iterrows():
        periods = main.pd.date_range(start=row["entry_time"], end=row["exit_time"], freq="h").tolist()
        for period in periods:
            occupied_periods.append({"timestamp": period})

    # Create DataFrame of occupied periods
    periods_df = main.pd.DataFrame(occupied_periods)

    # Count the number of tickets active per hour
    hourly_df = periods_df.groupby("timestamp").size().reset_index(name="tickets_active")

    # Align timestamps to hour intervals
    hourly_df["timestamp"] = hourly_df["timestamp"].dt.floor("h")

    # Create final DataFrame
    result_df = hourly_df.rename(columns={"timestamp": "period_start"})
    result_df["period_end"] = result_df["period_start"] + main.datetime.timedelta(hours=1)

    # Add additional time-related columns
    result_df["day_of_week"] = result_df["period_start"].dt.weekday
    result_df["hour"] = result_df["period_start"].dt.hour
    result_df["occupation_ratio"] = result_df["tickets_active"] / total_capacity

    if result_df.empty:
        return main.jsonify({"error": "No data available for the given period."}), 404

    # Generate a complete table with all day_of_week and hour combinations
    full_range = main.pd.date_range(start=result_df["period_start"].min(), 
                                    end=result_df["period_start"].max(), 
                                    freq="h")
    full_timeline = main.pd.DataFrame({
        "period_start": full_range,
        "day_of_week": full_range.weekday,
        "hour": full_range.hour
    })

    if full_timeline.empty:
        return main.jsonify({"error": "Timeline generation failed."}), 404

    # Merge result_df into the complete timeline, filling missing values with 0
    complete_df = full_timeline.merge(result_df, on=["period_start", "day_of_week", "hour"], how="left")
    complete_df["tickets_active"] = complete_df["tickets_active"].fillna(0)
    complete_df["occupation_ratio"] = complete_df["occupation_ratio"].fillna(0)

    # Calculate average occupation by day_of_week and hour
    summary_df = complete_df.groupby(["day_of_week", "hour"]).agg({
        "occupation_ratio": "mean"
    }).reset_index()

    summary_df = summary_df.rename(columns={"occupation_ratio": "predicted_occupation_probability"})
    if summary_df.empty:
        return main.jsonify({"error": "Summary generation failed."}), 404

    # Predict next 3 days based on current day
    current_day = main.datetime.datetime.now().weekday()
    predictions = []

    for i in range(3):  # Predict for the next 3 days
        target_day = (current_day + i) % 7
        target_date = (main.datetime.datetime.now() + main.datetime.timedelta(days=i)).strftime("%Y-%m-%d")

        # Generar intervals de 3 hores (0-3, 3-6, ..., 21-24)
        for start_hour in range(0, 24, 3):
            end_hour = start_hour + 3

            # Buscar les dades històriques per a aquest interval
            interval_rows = summary_df[
                (summary_df["day_of_week"] == target_day) &
                (summary_df["hour"] >= start_hour) &
                (summary_df["hour"] < end_hour)
            ]

            # Calcular la mitjana per a aquest interval (o 0 si no hi ha dades)
            predicted_probability = (
                interval_rows["predicted_occupation_probability"].mean()
                if not interval_rows.empty
                else 0
            )

            # Afegir la predicció per al bloc
            predictions.append({
                "day": target_date,
                "hour": f"{start_hour:02d}:00-{end_hour:02d}:00",
                "predicted_occupation_probability": round(predicted_probability, 2)
            })

    return main.jsonify(predictions)
