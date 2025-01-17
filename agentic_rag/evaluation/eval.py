import csv
import time
import requests
import json

# Paths for reading the original CSV and writing the updated file
endpoints_list = ["http://127.0.0.1:8000/orders/my", "http://127.0.0.1:8000/reviews/my", "http://127.0.0.1:8000/cart/my", "http://127.0.0.1:8000/orders/place", "http://127.0.0.1:8000/reviews/post", "http://127.0.0.1:8000/cart/add"]
csv_path = "test_queries.csv"

total_correct_endpoints = 0
total_retrieved_endpoints = 0
correct_retrieved_endpoints = 0
accurate_retrievals = 0

# Open the input CSV and read its contents
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    first_row = next(reader)
    fieldnames = first_row.keys() 
    num_queries = 28 #put formula here

    # Adding a new column for correctness check
    for row in reader:
        time.sleep(2)
        # Encode the query for URL
        query = row["QUERIES"]
        encoded_query = requests.utils.quote(query)
        correct_endpoints_boolean = json.loads(row["ENDPOINTS"])
        total_correct_endpoints += correct_endpoints_boolean.count(1)

        # Send the GET request with the query
        url = f"http://localhost:5000/query/retrieve?query={encoded_query}"
        response = requests.post(url)
        
        # Verify response status and correctness
        if response.status_code == 200:
            # Expected URLs based on CSV row values
            expected_urls = []
            for i in range(len(endpoints_list)):
                if correct_endpoints_boolean[i] == 1:
                    expected_urls.append(endpoints_list[i])
            print("correct = ", expected_urls, end="\n")
            print("retreived = ", response.json(), end="\n")
            
            correct_retrieved_endpoints += len(set(expected_urls) & set(response.json()))
            accurate_retrievals += (expected_urls == response.json())
            total_retrieved_endpoints += len(response.json())
            print(query, correct_retrieved_endpoints)
        else:
            row["Correct"] = "Request Failed"  # Handle failed requests

context_precision = correct_retrieved_endpoints/total_retrieved_endpoints
context_recall = correct_retrieved_endpoints/total_correct_endpoints
F1_score = (2*(context_precision*context_recall))/(context_precision+context_recall)
accuracy_score = accurate_retrievals/num_queries

# Define the file path where you want to save the metrics
output_csv_path = "metrics_results.csv"

# Data to save
metrics_data = {
    "Context Precision": context_precision,
    "Context Recall": context_recall,
    "F1 Score": F1_score,
    "Accuracy Score": accuracy_score
}

# Save metrics to a CSV file
with open(output_csv_path, mode='a', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=metrics_data.keys())
    writer.writerow(metrics_data)