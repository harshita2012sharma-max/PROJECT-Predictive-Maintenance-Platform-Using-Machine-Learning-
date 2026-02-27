def calculate_roi(downtime_cost_per_day, predicted_days_saved):
    
    saved_amount = downtime_cost_per_day * predicted_days_saved
    return float(saved_amount)