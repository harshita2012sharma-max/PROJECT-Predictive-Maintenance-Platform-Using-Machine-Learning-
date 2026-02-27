import mysql.connector
from mysql.connector import Error
from config.config import DB_CONFIG
from database.db_connection import execute_query


def create_database():
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        conn.commit()
        print("Database ready.")

    except Error as e:
        print(f"Error creating database: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def create_tables():

    tables = {

        "machines": """
        CREATE TABLE IF NOT EXISTS machines (
            machine_id INT AUTO_INCREMENT PRIMARY KEY,
            machine_name VARCHAR(100) NOT NULL,
            machine_type VARCHAR(100) NOT NULL,
            location VARCHAR(100),
            equipment_age FLOAT NOT NULL,
            criticality VARCHAR(20) NOT NULL,
            installation_date DATE,
            last_serviced DATE
        )
        """,

        "sensor_readings": """
CREATE TABLE IF NOT EXISTS sensor_readings (
    reading_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    machine_id INT NOT NULL,
    reading_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature FLOAT NOT NULL,
    vibration FLOAT NOT NULL,
    pressure FLOAT NOT NULL,
    rpm FLOAT NOT NULL,
    power_consumption FLOAT NOT NULL,
    oil_quality_index FLOAT NOT NULL,
    noise_level FLOAT NOT NULL,
    operating_hours FLOAT NOT NULL,
    production_load FLOAT NOT NULL,
    equipment_age FLOAT NOT NULL,
    will_fail TINYINT(1) NOT NULL,
    days_until_failure FLOAT NOT NULL,
    priority_label INT NOT NULL
)
""",

        "failure_history" : """
        CREATE TABLE IF NOT EXISTS failure_history (
            failure_id INT AUTO_INCREMENT PRIMARY KEY,
            machine_id INT NOT NULL,
            failure_date DATETIME NOT NULL,
            failed_component VARCHAR(100),
            failure_type VARCHAR(100),
            downtime_hours FLOAT,
            repair_cost DECIMAL(12,2),
            notes TEXT,
            FOREIGN KEY (machine_id)
                REFERENCES machines(machine_id)
                ON DELETE CASCADE
        )
        """,

        "failure_predictions": """
        CREATE TABLE IF NOT EXISTS failure_predictions (
            prediction_id INT AUTO_INCREMENT PRIMARY KEY,
            machine_id INT NOT NULL,
            reading_id BIGINT NOT NULL,
            predicted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            will_fail TINYINT(1) NOT NULL,
            failure_probability FLOAT NOT NULL,
            model_used VARCHAR(50),
            FOREIGN KEY (machine_id)
                REFERENCES machines(machine_id)
                ON DELETE CASCADE,
            FOREIGN KEY (reading_id)
                REFERENCES sensor_readings(reading_id)
                ON DELETE CASCADE
        )
        """,

        "rul_predictions": """
        CREATE TABLE IF NOT EXISTS rul_predictions (
            rul_id INT AUTO_INCREMENT PRIMARY KEY,
            machine_id INT NOT NULL,
            reading_id BIGINT NOT NULL,
            predicted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            days_until_failure FLOAT NOT NULL,
            confidence FLOAT,
            estimated_fail_date DATE,
            model_used VARCHAR(50),
            FOREIGN KEY (machine_id)
                REFERENCES machines(machine_id)
                ON DELETE CASCADE,
            FOREIGN KEY (reading_id)
                REFERENCES sensor_readings(reading_id)
                ON DELETE CASCADE
        )
        """,

        "maintenance_priority": """
        CREATE TABLE IF NOT EXISTS maintenance_priority (
            priority_id INT AUTO_INCREMENT PRIMARY KEY,
            machine_id INT NOT NULL,
            predicted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            priority_label VARCHAR(20) NOT NULL,
            priority_score FLOAT,
            recommended_by DATE,
            status VARCHAR(20) DEFAULT 'Pending',
            model_used VARCHAR(50),
            FOREIGN KEY (machine_id)
                REFERENCES machines(machine_id)
                ON DELETE CASCADE
        )
        """
    }

    for name, ddl in tables.items():
        execute_query(ddl)
        print(f" Table created: {name}")


if __name__ == "__main__":
    create_database()
    create_tables()
    print("\n Database setup complete.")