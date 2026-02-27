import pandas as pd
from database.db_connection import execute_query


def fetch_training_data():
    """Fetch all sensor readings - returns list of dictionaries"""
    query = "SELECT * FROM sensor_readings ORDER BY reading_id DESC"
    data = execute_query(query, fetch=True)
    return data  


def ensure_machine_exists(machine_id):
    """Make sure machine exists in machines table"""
    check_query = "SELECT machine_id FROM machines WHERE machine_id = %s"
    result = execute_query(check_query, (machine_id,), fetch=True)
    
    if not result:
        insert_query = """
            INSERT INTO machines (machine_id, machine_name, machine_type, equipment_age, criticality)
            VALUES (%s, %s, %s, %s, %s)
        """
        execute_query(insert_query, (
            machine_id,
            f"Machine {machine_id}",
            "Industrial Equipment",
            0,
            "Medium"
        ))
        print(f"Created machine record for machine_id {machine_id}")


def insert_sensor_reading(values):
    query = """
        INSERT INTO sensor_readings (
            machine_id, temperature, vibration, pressure, rpm,
            power_consumption, oil_quality_index, noise_level,
            operating_hours, production_load, equipment_age,
            will_fail, days_until_failure, priority_label
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    conn = None
    cursor = None
    try:
        from database.db_connection import get_connection
        
        # Ensure machine exists first
        machine_id = values[0]
        ensure_machine_exists(machine_id)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        reading_id = cursor.lastrowid
        print(f"DEBUG: Inserted sensor reading_id = {reading_id}")
        return reading_id
    except Exception as e:
        print(f"Database insert error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def get_latest_reading(machine_id):
    query = """
        SELECT * FROM sensor_readings
        WHERE machine_id = %s
        ORDER BY reading_timestamp DESC
        LIMIT 1
    """
    result = execute_query(query, (machine_id,), fetch=True)
    return result[0] if result else None


def save_failure_prediction(machine_id, reading_id, will_fail, probability):
    query = """
        INSERT INTO failure_predictions (
            machine_id, reading_id, will_fail, failure_probability, model_used
        )
        VALUES (%s,%s,%s,%s,%s)
    """
    return execute_query(query, (machine_id, reading_id, will_fail, probability, "LogisticRegression"))


def save_rul_prediction(machine_id, reading_id, days_remaining):
    query = """
        INSERT INTO rul_predictions (
            machine_id, reading_id, days_until_failure, model_used
        )
        VALUES (%s,%s,%s,%s)
    """
    return execute_query(query, (machine_id, reading_id, days_remaining, "LinearRegression"))


def save_priority(machine_id, label, score):
    query = """
        INSERT INTO maintenance_priority (
            machine_id, priority_label, priority_score, model_used
        )
        VALUES (%s,%s,%s,%s)
    """
    return execute_query(query, (machine_id, label, score, "DecisionTree"))
