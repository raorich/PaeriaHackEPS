import main
import logs
import numpy as np

def predict_parking_occupation():
    # Parse input data
    data = main.request.get_json()
    parking_id = data.get("parking_id")

    if not parking_id:
        return main.jsonify({"error": "parking_id is required"}), 400

    # Query historical data for the given parking ID
    history_data = main.History.query.filter_by(parking_id=parking_id).all()

    if not history_data:
        return main.jsonify([])

    # Convert query results to a DataFrame
    df = main.pd.DataFrame([{
        "timestamp": record.date,
        "ticket_id": record.ticket_id,
        "door_register_id": record.door_register_id
    } for record in history_data])

    if df.empty:
        return main.jsonify({"error": "No data available for this parking."}), 404

    df = df.sort_values("timestamp")
    door_types = {1: "entry", 2: "exit"}  # Assuming type_id = 1 is Entry, 2 is Exit

    # Fetch the door register data and convert it to a DataFrame
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

    if door_registers_df.empty:
        return main.jsonify({"error": "No matching door registers found."}), 404

    # Merge the DataFrames
    df = df.merge(door_registers_df, on="door_register_id")
    df["type"] = df["type_id"].map(door_types)
    df = df.drop_duplicates(subset=["ticket_id", "type"], keep="first")

    # Pivot to align entry and exit times by ticket_id
    try:
        pivoted = df.pivot(index="ticket_id", columns="type", values="timestamp").reset_index()
    except ValueError as e:
        return main.jsonify({"error": f"Error during pivot operation: {str(e)}"}), 500

    if "entry" not in pivoted.columns or "exit" not in pivoted.columns:
        return main.jsonify({"error": "Incomplete data: missing entries or exits for some tickets."}), 400

    # Calculate occupied time
    pivoted["occupied_time"] = (pivoted["exit"] - pivoted["entry"]).dt.total_seconds() / 3600  # Hours occupied

    # Expand to hourly granularity
    occupied_periods = []
    for _, row in pivoted.iterrows():
        if main.pd.notna(row["entry"]) and main.pd.notna(row["exit"]):
            occupied_periods.extend(main.pd.date_range(start=row["entry"], end=row["exit"], freq="h").tolist())

    hourly_df = main.pd.DataFrame({"timestamp": occupied_periods})
    hourly_df = hourly_df.groupby("timestamp").size().reset_index(name="occupied_slots")
    hourly_df["day_of_week"] = hourly_df["timestamp"].dt.weekday
    hourly_df["hour"] = hourly_df["timestamp"].dt.hour

    # Normalize and smooth historical data
    hourly_df["occupied_slots"] = hourly_df["occupied_slots"].astype(float)
    max_slots = hourly_df["occupied_slots"].max()

    # Debugging max_slots
    if max_slots == 0:
        print("Error: max_slots is 0, indicating no occupation data.")
        return main.jsonify({"error": "No valid historical data to make predictions."}), 400

    hourly_df["normalized_occupation"] = hourly_df["occupied_slots"] / max_slots

    # Debugging normalized values
    print("Normalized occupation values:")
    print(hourly_df["normalized_occupation"].describe())

    # Prepare predictions for the next 7 days
    current_time = main.datetime.datetime.now()
    predictions = []

    for i in range(7):  # For each of the next 7 days
        target_time = current_time + main.datetime.timedelta(days=i)
        target_day_of_week = target_time.weekday()

        historical_data = hourly_df[hourly_df["day_of_week"] == target_day_of_week]

        if historical_data.empty:
            continue

        hour_occupation = (
            historical_data.groupby("hour")["normalized_occupation"]
            .mean()
            .reset_index()
        )

        for hour in range(24):
            prediction = hour_occupation[hour_occupation["hour"] == hour]["normalized_occupation"]
            prediction = prediction.iloc[0] if not prediction.empty else 0

            # Debugging individual predictions
            print(f"Prediction for day {target_time.strftime('%Y-%m-%d')}, hour {hour}: {prediction}")

            predictions.append({
                "hour": hour,
                "day": target_time.strftime("%Y-%m-%d"),
                "predicted_occupation_probability": round(prediction, 2),  # Probability (0.0 to 1.0)
            })

    print(predictions)
    return main.jsonify(predictions)


def predict_parking_occupation_old():
    # Parse input data
    data = main.request.get_json()
    parking_id = data.get("parking_id")

    if not parking_id:
        return main.jsonify({"error": "parking_id is required"}), 400

    # Query historical data for the given parking ID
    history_data = main.History.query.filter_by(parking_id=parking_id).all()

    if not history_data:
        return main.jsonify([])

    # Convert query results to a DataFrame
    df = main.pd.DataFrame([{
        "timestamp": record.date,
        "ticket_id": record.ticket_id,
        "door_register_id": record.door_register_id
    } for record in history_data])

    if df.empty:
        return main.jsonify({"error": "No data available for this parking."}), 404

    df = df.sort_values("timestamp")
    door_types = {1: "entry", 2: "exit"}  # Assuming type_id = 1 is Entry, 2 is Exit

    # Fetch the door register data and convert it to a DataFrame
    door_registers = main.DoorRegisters.query.filter(
        main.DoorRegisters.id.in_(df['door_register_id'])
    ).with_entities(
        main.DoorRegisters.id.label('door_register_id'),
        main.DoorRegisters.type_id.label('type_id')
    ).all()

    # Convert the query result to a DataFrame
    door_registers_df = main.pd.DataFrame([{
        "door_register_id": record.door_register_id,
        "type_id": record.type_id
    } for record in door_registers])

    if door_registers_df.empty:
        return main.jsonify({"error": "No matching door registers found."}), 404

    # Merge the DataFrames
    df = df.merge(door_registers_df, on="door_register_id")

    # Map type_id to 'entry' or 'exit'
    df["type"] = df["type_id"].map(door_types)

    # Ensure there is only one entry and one exit per ticket_id
    df = df.drop_duplicates(subset=["ticket_id", "type"], keep="first")

    # Pivot to align entry and exit times by ticket_id
    try:
        pivoted = df.pivot(index="ticket_id", columns="type", values="timestamp").reset_index()
    except ValueError as e:
        return main.jsonify({"error": f"Error during pivot operation: {str(e)}"}), 500

    # Ensure there are valid entries and exits
    if "entry" not in pivoted.columns or "exit" not in pivoted.columns:
        return main.jsonify({"error": "Incomplete data: missing entries or exits for some tickets."}), 400

    # Calculate occupied time
    pivoted["occupied_time"] = (pivoted["exit"] - pivoted["entry"]).dt.total_seconds() / 3600  # Hours occupied

    # Expand to hourly granularity
    occupied_periods = []
    for _, row in pivoted.iterrows():
        if main.pd.notna(row["entry"]) and main.pd.notna(row["exit"]):
            occupied_periods.extend(main.pd.date_range(start=row["entry"], end=row["exit"], freq="h").tolist())

    # Create a DataFrame of hourly timestamps with occupation count
    hourly_df = main.pd.DataFrame({"timestamp": occupied_periods})
    hourly_df = hourly_df.groupby("timestamp").size().reset_index(name="occupied_slots")

    # Extract day of week and hour for grouping
    hourly_df["day_of_week"] = hourly_df["timestamp"].dt.weekday
    hourly_df["hour"] = hourly_df["timestamp"].dt.hour

    # Prepare predictions for the next 7 days
    current_time = main.datetime.datetime.now()
    predictions = []

    for i in range(7):  # For each of the next 7 days
        target_time = current_time + main.datetime.timedelta(days=i)
        target_day_of_week = target_time.weekday()

        # Filter historical data for the same day of the week
        historical_data = hourly_df[hourly_df["day_of_week"] == target_day_of_week]

        if historical_data.empty:
            continue

        # Calculate average occupied slots for each hour
        hour_occupation = (
            historical_data.groupby("hour")["occupied_slots"]
            .mean()
            .reset_index()
        )

        # Generate predictions for each hour
        for hour in range(24):
            prediction = hour_occupation[hour_occupation["hour"] == hour]["occupied_slots"]
            prediction = prediction.iloc[0] if not prediction.empty else 0

            predictions.append({
                "hour": hour,
                "day": target_time.strftime("%Y-%m-%d"),
                "predicted_occupied_slots": prediction,
            })

    # Return the predictions
    return main.jsonify(predictions)
