from flask import Flask, jsonify, request, Response
import uuid
import math
from datetime import datetime

app = Flask(__name__)

cache = {}

@app.route("/receipts/process", methods=['POST'])
def process():
    body = request.get_json()
    try:
        body["points"] = process_receipt(body)
    except:
        return "The receipt is invalid", 400
    receipt_id = str(uuid.uuid4())
    cache[receipt_id] = body

    return jsonify({
        'id': receipt_id
    })

@app.route("/receipts/<receipt_id>/points")
def get_points(receipt_id):
    #400 if receipt not found
    if receipt_id not in cache.keys():
        return "No receipt found for that id", 404
    
    return jsonify({
        "points": cache[receipt_id]["points"]
    })

def process_receipt(receipt):
    points = 0

    #round $ amount is inherently a multiple of $.25 so just add 75 rather than 50+25
    if float(receipt["total"]) % 1 == 0:
        points += 75
    elif float(receipt["total"]) % .25 == 0:
        points += 25
    
    #points for day of month being even
    if int(receipt["purchaseDate"].split('-')[2]) % 2 == 1:
        points += 6
    
    #start and end times for comparing purchaseTime
    start_time = datetime.strptime("14:00", "%H:%M")
    end_time = datetime.strptime("16:00", "%H:%M")
    if datetime.strptime(receipt["purchaseTime"], "%H:%M") > start_time and datetime.strptime(receipt["purchaseTime"], "%H:%M") < end_time:
        points += 10 
    
    #Count the number of alphanumeric characters in the retailer name
    retailer_chars = sum(char.isalnum() for char in receipt["retailer"])
    points += retailer_chars
    
    #points for numbe of chars in item description being multiple of 3
    for item in receipt["items"]:
        if len(item["shortDescription"].strip()) % 3 == 0:
            points += math.ceil(.2 * float(item["price"]))
    
    #5 points for every 2 items
    points += 5 * (len(receipt["items"])//2)

    return points