# app.py
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from storage import load_tasks_linked, save_tasks_linked, Task, next_id
import scheduler
import os

app = Flask(__name__, static_folder="public", static_url_path="")
CORS(app)

linked = load_tasks_linked()

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

# Generic simulate endpoint
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
                return jsonify({"error": "quantum required for Round Robin"}), 400
            res = scheduler.round_robin(tasks, float(quantum))
        else:
            return jsonify({"error": "unknown algorithm"}), 400
        return jsonify({"algorithm": algorithm, "result": res})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Convenience endpoints: one per algorithm
@app.route("/api/simulate/fcfs", methods=["GET","POST"])
def sim_fcfs():
    tasks = [t.to_dict() for t in linked.to_list()]
    for x in tasks:
        x["burst"] = float(x["burst"])
        x["arrival"] = float(x["arrival"])
        x["priority"] = int(x.get("priority", 0))
        x["id"] = int(x["id"])
    return jsonify({"algorithm":"FCFS","result": scheduler.fcfs(tasks)})

@app.route("/api/simulate/sjf", methods=["GET","POST"])
def sim_sjf():
    tasks = [t.to_dict() for t in linked.to_list()]
    for x in tasks:
        x["burst"] = float(x["burst"])
        x["arrival"] = float(x["arrival"])
        x["priority"] = int(x.get("priority", 0))
        x["id"] = int(x["id"])
    return jsonify({"algorithm":"SJF","result": scheduler.sjf(tasks)})

@app.route("/api/simulate/priority", methods=["GET","POST"])
def sim_priority():
    tasks = [t.to_dict() for t in linked.to_list()]
    for x in tasks:
        x["burst"] = float(x["burst"])
        x["arrival"] = float(x["arrival"])
        x["priority"] = int(x.get("priority", 0))
        x["id"] = int(x["id"])
    return jsonify({"algorithm":"Priority","result": scheduler.priority_scheduling(tasks)})

@app.route("/api/simulate/rr", methods=["POST"])
def sim_rr():
    data = request.get_json(force=True)
    quantum = data.get("quantum", None)
    if quantum is None:
        return jsonify({"error":"quantum required"}), 400
    tasks = [t.to_dict() for t in linked.to_list()]
    for x in tasks:
        x["burst"] = float(x["burst"])
        x["arrival"] = float(x["arrival"])
        x["priority"] = int(x.get("priority", 0))
        x["id"] = int(x["id"])
    return jsonify({"algorithm":"RoundRobin","result": scheduler.round_robin(tasks, float(quantum))})

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join("public", path)):
        return send_from_directory("public", path)
    return send_from_directory("public", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
