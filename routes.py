from flask import render_template, request
from database.data_access import insert_sensor_reading, fetch_training_data
from services.prediction_service import run_prediction
from services.alert_service import check_alert
from config.config import SENSOR_FEATURES


def register_routes(app):
    
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/analytics")
    def analytics():
        try:
            # Fetch data from database
            data = fetch_training_data()
            
            # If no data, show empty state
            if not data:
                return render_template("analytics.html",
                    total_machines=0,
                    critical_count=0,
                    avg_health=0,
                    prevented_failures=0,
                    recent_data=[],
                    has_data=False,
                    temp_data=[0,0,0,0],
                    priority_data=[0,0,0,0],
                    rul_labels=[],
                    rul_values=[])
            
            # Calculate KPIs
            machines = set(row['machine_id'] for row in data)
            total_machines = len(machines)
            
            critical_count = sum(1 for row in data if row.get('priority_label') == 3)
            
            healthy = sum(1 for row in data if row.get('will_fail') == 0)
            avg_health = (healthy / len(data) * 100) if data else 0
            
            prevented_failures = sum(1 for row in data if row.get('will_fail') == 1)
            
            # CHART DATA 
            
            # 1. Temperature Distribution
            temp_data = [0, 0, 0, 0]  
            for row in data:
                temp = row.get('temperature', 0)
                if temp < 75:
                    temp_data[0] += 1  
                elif temp < 85:
                    temp_data[1] += 1  
                elif temp < 95:
                    temp_data[2] += 1  
                else:
                    temp_data[3] += 1 
            
            # 2. Priority Distribution
            priority_data = [0, 0, 0, 0]  
            for row in data:
                priority = row.get('priority_label', 0)
                if 0 <= priority <= 3:
                    priority_data[priority] += 1
            
            # 3. RUL Chart - Latest prediction per machine
            machine_rul = {}
            for row in data:
                machine_id = row.get('machine_id')
                reading_id = row.get('reading_id', 0)
                
                if machine_id not in machine_rul or reading_id > machine_rul[machine_id]['reading_id']:
                    machine_rul[machine_id] = {
                        'reading_id': reading_id,
                        'rul': row.get('days_until_failure', 0)
                    }
            
            rul_labels = []
            rul_values = []
            for machine_id in sorted(machine_rul.keys()):
                rul_labels.append(f"Machine {machine_id}")
                rul_values.append(int(machine_rul[machine_id]['rul']))
            
            # Recent Predictions Table
            recent_data = []
            sorted_data = sorted(data, key=lambda x: x.get('reading_id', 0), reverse=True)
            
            for row in sorted_data[:10]:
                priority_names = {0: "Low", 1: "Medium", 2: "High", 3: "Critical"}
                fail_prob = row.get('will_fail', 0) * 100
                
                recent_data.append({
                    'machine_id': row.get('machine_id', 'N/A'),
                    'timestamp': str(row.get('reading_timestamp', 'N/A'))[:16],
                    'failure_prob': fail_prob,
                    'days': int(row.get('days_until_failure', 0)),
                    'priority': priority_names.get(row.get('priority_label', 0), 'Low'),
                    'status': 'Critical' if fail_prob > 70 else 'At Risk' if fail_prob > 40 else 'Healthy'
                })
            
            return render_template("analytics.html",
                total_machines=total_machines,
                critical_count=critical_count,
                avg_health=round(avg_health, 1),
                prevented_failures=prevented_failures,
                recent_data=recent_data,
                has_data=True,
                temp_data=temp_data,
                priority_data=priority_data,
                rul_labels=rul_labels,
                rul_values=rul_values)
                
        except Exception as e:
            print(f"Analytics error: {e}")
            import traceback
            traceback.print_exc()
            
            return render_template("analytics.html",
                total_machines=0,
                critical_count=0,
                avg_health=0,
                prevented_failures=0,
                recent_data=[],
                has_data=False,
                temp_data=[0,0,0,0],
                priority_data=[0,0,0,0],
                rul_labels=[],
                rul_values=[])

    @app.route("/predict", methods=["POST"])
    def predict():
        machine_id = int(request.form.get("machine_id", 1))
        input_data = {}

        for feature in SENSOR_FEATURES:
            value = request.form.get(feature)
            if not value:
                return render_template("index.html", error=f"{feature} is required")
            try:
                input_data[feature] = float(value)
            except:
                return render_template("index.html", error=f"{feature} must be a number")
        
        reading_id = insert_sensor_reading((machine_id, *input_data.values(), 0, 0, 0))
        if not reading_id:
            return render_template("index.html", error="Database error")

        prediction = run_prediction(machine_id, reading_id, input_data)
        if not prediction:
            return render_template("index.html", 
                error="Prediction failed. Train models first: python -m training.train",
                machine_id=machine_id)

        alert = check_alert(prediction["failure_probability"], prediction["days_until_failure"])

        return render_template("index.html",
            result=prediction,
            alert=alert,
            machine_id=machine_id,
            success=True)