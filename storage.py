# storage.py
import json
import os
from typing import Optional, List

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")

class Task:
    def __init__(self, id: int, name: str, burst: float, arrival: float, priority: int):
        self.id = id
        self.name = name
        self.burst = float(burst)
        self.arrival = float(arrival)
        self.priority = int(priority)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "burst": self.burst,
            "arrival": self.arrival,
            "priority": self.priority
        }

    @staticmethod
    def from_dict(d):
        return Task(int(d["id"]), d["name"], float(d["burst"]), float(d["arrival"]), int(d.get("priority", 0)))

class Node:
    def __init__(self, task: Task):
        self.task = task
        self.prev: Optional["Node"] = None
        self.next: Optional["Node"] = None

class LinkedTaskList:
    def __init__(self):
        self.head: Optional[Node] = None

    def insert_ordered(self, t: Task):
        n = Node(t)
        if not self.head:
            self.head = n
            return True
        cur = self.head
        if t.id < cur.task.id:
            n.next = cur
            cur.prev = n
            self.head = n
            return True
        while cur.next and cur.next.task.id < t.id:
            cur = cur.next
        if cur.task.id == t.id or (cur.next and cur.next.task.id == t.id):
            return False
        n.next = cur.next
        n.prev = cur
        if cur.next:
            cur.next.prev = n
        cur.next = n
        return True

    def find_by_id(self, id: int):
        cur = self.head
        while cur:
            if cur.task.id == id:
                return cur.task
            cur = cur.next
        return None

    def delete_by_id(self, id: int):
        cur = self.head
        while cur and cur.task.id != id:
            cur = cur.next
        if not cur:
            return False
        if cur.prev:
            cur.prev.next = cur.next
        else:
            self.head = cur.next
        if cur.next:
            cur.next.prev = cur.prev
        return True

    def find_by_priority(self, priority: int, limit: int = 64):
        out = []
        cur = self.head
        while cur and len(out) < limit:
            if cur.task.priority == priority:
                out.append(cur.task)
            cur = cur.next
        return out

    def to_list(self):
        out = []
        cur = self.head
        while cur:
            out.append(cur.task)
            cur = cur.next
        return out

    def clear(self):
        self.head = None

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_tasks_linked(linked: LinkedTaskList):
    ensure_data_dir()
    arr = [t.to_dict() for t in linked.to_list()]
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(arr, f, indent=2)

def load_tasks_linked() -> LinkedTaskList:
    linked = LinkedTaskList()
    ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf8") as f:
            json.dump([], f)
        return linked
    try:
        with open(DATA_FILE, "r", encoding="utf8") as f:
            arr = json.load(f)
        arr_sorted = sorted(arr, key=lambda d: int(d["id"]))
        for d in arr_sorted:
            t = Task.from_dict(d)
            linked.insert_ordered(t)
    except Exception as e:
        print("Failed to load tasks:", e)
    return linked

def next_id(linked: LinkedTaskList) -> int:
    max_id = 0
    cur = linked.head
    while cur:
        if cur.task.id > max_id:
            max_id = cur.task.id
        cur = cur.next
    return max_id + 1
