from flask import Flask, jsonify, request
import uuid
import math
from datetime import datetime

app = Flask(__name__)

cache = {}

@app.route("/receipts/process", methods=['POST'])
def process():
    body = request.get_json()
    receipt_id = str(uuid.uuid4())
    cache[receipt_id] = body

    return jsonify({
        'id': receipt_id
    })

@app.route("/receipts/<receipt_id>/points")
def get_points(receipt_id):
    receipt = cache[receipt_id]
    points = 0

    if float(receipt["total"]) % 1 == 0:
        points += 75
    elif float(receipt["total"]) % .25 == 0:
        points += 25
    if int(receipt["purchaseDate"].split('-')[2]) % 2 == 1:
        points += 6
    time_2 = datetime.strptime("14:00", "%H:%M")
    time_4 = datetime.strptime("16:00", "%H:%M")
    if datetime.strptime(receipt["purchaseTime"], "%H:%M") > time_2 and datetime.strptime(receipt["purchaseTime"], "%H:%M") < time_4:
        points += 10 
    
    #Count the number of Alphanumeric characters in the retailer name
    retailer_chars = sum(char.isalnum() for char in receipt["retailer"])
    points += retailer_chars
    
    for item in receipt["items"]:
        if len(item["shortDescription"].strip()) % 3 == 0:
            points += math.ceil(.2 * float(item["price"]))
    
    points += 5 * (len(receipt["items"])//2)
    
    return jsonify({
        "points": points
    })