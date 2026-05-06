import os
import json
import redis
from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
CACHE_TTL = 30

try:
    cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    cache.ping()
    REDIS_AVAILABLE = True
except Exception:
    REDIS_AVAILABLE = False


def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "postgres"),
        database=os.environ.get("POSTGRES_DB", "taskdb"),
        user=os.environ.get("POSTGRES_USER", "appuser"),
        password=os.environ.get("POSTGRES_PASSWORD", "changeme")
    )


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            done BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "redis": REDIS_AVAILABLE})


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    if REDIS_AVAILABLE:
        cached = cache.get("tasks")
        if cached:
            return jsonify(json.loads(cached))

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = [dict(row) for row in cur.fetchall()]
    # convert datetime to string for JSON serialization
    for t in tasks:
        if t.get("created_at"):
            t["created_at"] = t["created_at"].isoformat()
    cur.close()
    conn.close()

    if REDIS_AVAILABLE:
        cache.setex("tasks", CACHE_TTL, json.dumps(tasks))

    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING *", (data["title"],))
    task = dict(cur.fetchone())
    if task.get("created_at"):
        task["created_at"] = task["created_at"].isoformat()
    conn.commit()
    cur.close()
    conn.close()

    if REDIS_AVAILABLE:
        cache.delete("tasks")

    return jsonify(task), 201


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def toggle_task(task_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("UPDATE tasks SET done = NOT done WHERE id = %s RETURNING *", (task_id,))
    task = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if task is None:
        return jsonify({"error": "not found"}), 404

    if REDIS_AVAILABLE:
        cache.delete("tasks")

    task = dict(task)
    if task.get("created_at"):
        task["created_at"] = task["created_at"].isoformat()
    return jsonify(task)


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()

    if REDIS_AVAILABLE:
        cache.delete("tasks")

    return jsonify({"deleted": task_id})


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
