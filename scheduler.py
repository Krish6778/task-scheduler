# scheduler.py
from typing import List, Dict
import math
import copy

def fcfs(tasks: List[Dict]) -> List[Dict]:
    t = copy.deepcopy(tasks)
    t.sort(key=lambda x: (x["arrival"], x["id"]))
    current = 0.0
    for task in t:
        if current < task["arrival"]:
            current = task["arrival"]
        task["waitingTime"] = current - task["arrival"]
        task["startTime"] = current
        current += task["burst"]
        task["turnaroundTime"] = task["waitingTime"] + task["burst"]
    return t

def sjf(tasks: List[Dict]) -> List[Dict]:
    n = len(tasks)
    t = copy.deepcopy(tasks)
    is_completed = [False] * n
    completed = 0
    current = 0.0
    # We'll compute start times as arrival + waiting
    while completed < n:
        idx = -1
        min_burst = math.inf
        for i in range(n):
            if not is_completed[i] and t[i]["arrival"] <= current:
                if t[i]["burst"] < min_burst:
                    min_burst = t[i]["burst"]
                    idx = i
                elif t[i]["burst"] == min_burst:
                    if t[i]["arrival"] < t[idx]["arrival"]:
                        idx = i
        if idx != -1:
            t[idx]["waitingTime"] = current - t[idx]["arrival"]
            t[idx]["startTime"] = current
            current += t[idx]["burst"]
            t[idx]["turnaroundTime"] = t[idx]["waitingTime"] + t[idx]["burst"]
            is_completed[idx] = True
            completed += 1
        else:
            current += 1.0
    return t

def round_robin(tasks: List[Dict], quantum: float) -> List[Dict]:
    if quantum <= 0:
        raise ValueError("quantum must be > 0")
    n = len(tasks)
    t = copy.deepcopy(tasks)
    remaining = [t[i]["burst"] for i in range(n)]
    visited = [False] * n
    queue = []
    current = 0.0
    completed = 0
    # initial enqueue
    for i in range(n):
        if t[i]["arrival"] <= current and not visited[i]:
            queue.append(i); visited[i] = True
    # we'll record first startTime when a task gets CPU for first time
    first_start = [None] * n
    while completed < n:
        if not queue:
            current += 1.0
            for i in range(n):
                if not visited[i] and t[i]["arrival"] <= current:
                    queue.append(i); visited[i] = True
            continue
        idx = queue.pop(0)
        if first_start[idx] is None:
            first_start[idx] = current
        if remaining[idx] > quantum:
            current += quantum
            remaining[idx] -= quantum
            for i in range(n):
                if (not visited[i]) and (t[i]["arrival"] > current - quantum) and (t[i]["arrival"] <= current):
                    queue.append(i); visited[i] = True
            queue.append(idx)
        else:
            current += remaining[idx]
            remaining[idx] = 0
            t[idx]["turnaroundTime"] = current - t[idx]["arrival"]
            t[idx]["waitingTime"] = t[idx]["turnaroundTime"] - t[idx]["burst"]
            completed += 1
            for i in range(n):
                if (not visited[i]) and (t[i]["arrival"] <= current):
                    queue.append(i); visited[i] = True
    # assign startTime as first_start or arrival if never started (rare)
    for i in range(n):
        t[i]["startTime"] = first_start[i] if first_start[i] is not None else t[i]["arrival"]
    return t

def priority_scheduling(tasks: List[Dict]) -> List[Dict]:
    n = len(tasks)
    t = copy.deepcopy(tasks)
    is_completed = [False] * n
    completed = 0
    current = 0.0
    while completed < n:
        idx = -1
        best_priority = math.inf
        for i in range(n):
            if not is_completed[i] and t[i]["arrival"] <= current:
                if t[i].get("priority", 0) < best_priority:
                    best_priority = t[i].get("priority", 0)
                    idx = i
                elif t[i].get("priority", 0) == best_priority:
                    if t[i]["arrival"] < t[idx]["arrival"]:
                        idx = i
        if idx != -1:
            t[idx]["waitingTime"] = current - t[idx]["arrival"]
            t[idx]["startTime"] = current
            current += t[idx]["burst"]
            t[idx]["turnaroundTime"] = t[idx]["waitingTime"] + t[idx]["burst"]
            is_completed[idx] = True
            completed += 1
        else:
            current += 1.0
    return t
