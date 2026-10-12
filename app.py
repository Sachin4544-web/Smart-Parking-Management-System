from flask import Flask, request, redirect, url_for
from datetime import datetime
import math

app = Flask(__name__)

# Temporary storage for parked vehicles
parked_vehicles = {}

# Parking history
parking_history = []

TOTAL_SLOTS = 10

# Parking rates per hour
RATES = {
    "Bike": 20,
    "Car": 50,
    "Truck": 100
}


@app.route("/", methods=["GET", "POST"])
def home():

    message = ""

    # Register a vehicle
    if request.method == "POST":

        vehicle_number = request.form.get(
            "vehicle_number", ""
        ).strip().upper()

        vehicle_type = request.form.get("vehicle_type", "")

        if not vehicle_number:
            message = "Please enter a vehicle number."

        elif vehicle_type not in RATES:
            message = "Invalid vehicle type."

        elif vehicle_number in parked_vehicles:
            message = "This vehicle is already parked!"

        elif len(parked_vehicles) >= TOTAL_SLOTS:
            message = "Parking is full!"

        else:

            occupied_slots = [
                v["slot"] for v in parked_vehicles.values()
            ]

            for slot in range(1, TOTAL_SLOTS + 1):

                if slot not in occupied_slots:

                    parked_vehicles[vehicle_number] = {
                        "type": vehicle_type,
                        "slot": slot,
                        "entry_time": datetime.now()
                    }

                    message = (
                        f"Vehicle parked successfully in Slot {slot}!"
                    )
                    break

    # Generate parking slots
    slots = ""

    for i in range(1, TOTAL_SLOTS + 1):

        vehicle = next(
            (
                (number, data)
                for number, data in parked_vehicles.items()
                if data["slot"] == i
            ),
            None
        )

        if vehicle:

            number, data = vehicle

            color = "#f8d7da"

            status = f"""
                <p>Occupied</p>
                <p>{number}</p>
                <p>{data['type']}</p>

                <form action="/exit/{number}" method="POST">
                    <button type="submit">Vehicle Exit</button>
                </form>
            """

        else:

            color = "#d4edda"
            status = "<p>Available</p>"

        slots += f"""
        <div style="
            background:{color};
            width:150px;
            padding:15px;
            margin:10px;
            border-radius:10px;
            display:inline-block;
        ">
            <h3>Slot {i}</h3>
            {status}
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Parking System</title>
    </head>

    <body style="
        font-family:Arial;
        background:#f0f4f8;
        text-align:center;
        padding:20px;
    ">

        <h1>Smart Parking Management System</h1>

        <h2>Parking Dashboard</h2>

        <h3>
            Total Slots: {TOTAL_SLOTS}
            | Occupied: {len(parked_vehicles)}
            | Available: {TOTAL_SLOTS - len(parked_vehicles)}
        </h3>

        <h2>Register Vehicle</h2>

        <form method="POST">

            <input
                type="text"
                name="vehicle_number"
                placeholder="Enter vehicle number"
                required
            >

            <select name="vehicle_type" required>
                <option value="Bike">Bike</option>
                <option value="Car">Car</option>
                <option value="Truck">Truck</option>
            </select>

            <button type="submit">Park Vehicle</button>

        </form>

        <h3>{message}</h3>

        <h2>Parking Slots</h2>

        {slots}

        <br>

        <a href="/history">View Parking History</a>

    </body>
    </html>
    """


# Vehicle exit and fee calculation
@app.route("/exit/<vehicle_number>", methods=["POST"])
def vehicle_exit(vehicle_number):

    vehicle = parked_vehicles.get(vehicle_number)

    if vehicle is None:
        return "Vehicle not found!", 404

    exit_time = datetime.now()

    duration_seconds = (
        exit_time - vehicle["entry_time"]
    ).total_seconds()

    # Minimum charge: one hour
    hours = max(1, math.ceil(duration_seconds / 3600))

    rate = RATES[vehicle["type"]]

    fee = hours * rate

    # Save completed parking record
    parking_history.append({
        "vehicle_number": vehicle_number,
        "type": vehicle["type"],
        "slot": vehicle["slot"],
        "entry_time": vehicle["entry_time"].strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "exit_time": exit_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "hours": hours,
        "fee": fee
    })

    # Free the parking slot
    del parked_vehicles[vehicle_number]

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Parking Receipt</title>
    </head>

    <body style="
        font-family:Arial;
        text-align:center;
        background:#f0f4f8;
        padding:40px;
    ">

        <h1>Vehicle Exit Successful!</h1>

        <h2>Parking Receipt</h2>

        <p>Vehicle Number: {vehicle_number}</p>
        <p>Vehicle Type: {vehicle['type']}</p>
        <p>Parking Slot: {vehicle['slot']}</p>
        <p>Entry Time: {vehicle['entry_time']}</p>
        <p>Exit Time: {exit_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Charged Hours: {hours}</p>

        <h2>Parking Fee: ₹{fee}</h2>

        <a href="/">Back to Dashboard</a>

    </body>
    </html>
    """


# Parking history
@app.route("/history")
def history():

    rows = ""

    for record in reversed(parking_history):

        rows += f"""
        <tr>
            <td>{record['vehicle_number']}</td>
            <td>{record['type']}</td>
            <td>{record['slot']}</td>
            <td>{record['entry_time']}</td>
            <td>{record['exit_time']}</td>
            <td>{record['hours']}</td>
            <td>₹{record['fee']}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Parking History</title>
    </head>

    <body style="font-family:Arial;padding:30px">

        <h1>Parking History</h1>

        <table border="1" cellpadding="10" cellspacing="0">

            <tr>
                <th>Vehicle Number</th>
                <th>Type</th>
                <th>Slot</th>
                <th>Entry Time</th>
                <th>Exit Time</th>
                <th>Hours</th>
                <th>Fee</th>
            </tr>

            {rows}

        </table>

        <br>

        <a href="/">Back to Dashboard</a>

    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)