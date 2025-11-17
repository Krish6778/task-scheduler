from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from storage import load_tasks_linked, save_tasks_linked, Task, next_id
import scheduler
import os

# Serve static files from ROOT directory
app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

linked = load_tasks_linked()

# ---------------- TASK ROUTES ----------------

@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    arr = [t.to_dict() for t in linked.to_list()]
    return jsonify(arr)

@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json(force=True)
    name = data.get("name")
    burst = data.get("burst")
    arrival = data.get("arrival")
    priority = data.get("priority", 0)

    if name is None or burst is None or arrival is None:
        return jsonify({"error": "name, burst and arrival are required"}), 400

    tid = next_id(linked)
    t = Task(tid, name, burst, arrival, int(priority))

    ok = linked.insert_ordered(t)
    if not ok:
        return jsonify({"error": "duplicate id or insertion failed"}), 400

    save_tasks_linked(linked)
    return jsonify(t.to_dict())

@app.route("/api/tasks/<int:tid>", methods=["DELETE"])
def delete_task(tid):
    ok = linked.delete_by_id(tid)
    if not ok:
        return jsonify({"error": "not found"}), 404
    save_tasks_linked(linked)
    return jsonify({"deleted": tid})

# ---------------- SIMULATION ----------------

@app.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.get_json(force=True)
    algorithm = data.get("algorithm")
    quantum = data.get("quantum", None)

    tasks = [t.to_dict() for t in linked.to_list()]
    for x in tasks:
        x["burst"] = float(x["burst"])
        x["arrival"] = float(x["arrival"])
        x["priority"] = int(x.get("priority", 0))
        x["id"] = int(x["id"])

    if not algorithm:
        return jsonify({"error": "algorithm required"}), 400

    algo = algorithm.lower()

    try:
        if algo == "fcfs":
            res = scheduler.fcfs(tasks)
        elif algo == "sjf":
            res = scheduler.sjf(tasks)
        elif "priority" in algo:
            res = scheduler.priority_scheduling(tasks)
        elif "round" in algo or "rr" in algo:
            if quantum is None:
                return jsonify({"error": "quantum required"}), 400
            res = scheduler.round_robin(tasks, float(quantum))
        else:
            return jsonify({"error": "unknown algorithm"}), 400

        return jsonify({"algorithm": algorithm, "result": res})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- FRONTEND ROUTE ----------------
# Serve index.html and any file in ROOT

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(path):
        return send_from_directory(".", path)
    return send_from_directory(".", "index.html")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
