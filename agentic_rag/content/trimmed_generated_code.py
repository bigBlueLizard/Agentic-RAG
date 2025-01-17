def func(objects):
    total_sum = 0
    total_orders = 0
    for obj in objects:
        if obj.get("created_at") and obj["created_at"].startswith("2024-11"):
            total_sum += obj.get("total_amount", 0)
            total_orders += 1
    if total_orders == 0:
        return 0
    return total_sum / total_orders