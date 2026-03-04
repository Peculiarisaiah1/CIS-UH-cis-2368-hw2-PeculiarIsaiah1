from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# ------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="tickets-db.clog0eay43i9.us-east-2.rds.amazonaws.com",
        user="admin",
        password="Admin12345!",
        database="TicketDB",
        ssl_ca="global-bundle.pem"
    )

# ------------------------------------------------
# CREATE A JOB
# ------------------------------------------------
@app.route("/job", methods=["POST"])
def create_job():
    data = request.get_json()

    title = data.get("title")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not title or not start_date or not end_date:
        return jsonify({"error": "title, start_date, and end_date are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO jobs (title, start_date, end_date)
        VALUES (%s, %s, %s)
    """, (title, start_date, end_date))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Job created successfully"}), 201

# ------------------------------------------------
# GET ALL JOBS
# ------------------------------------------------
@app.route("/jobs", methods=["GET"])
def get_jobs():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM jobs")
    jobs = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(jobs), 200

# ------------------------------------------------
# DELETE A JOB
# ------------------------------------------------
@app.route("/job/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
    conn.commit()

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        return jsonify({"error": "Job not found"}), 404

    cur.close()
    conn.close()
    return jsonify({"message": "Job deleted successfully"}), 200

# ------------------------------------------------
# CREATE ASSIGNMENT (WITH DATE OVERLAP CHECK)
# ------------------------------------------------
@app.route("/assignment", methods=["POST"])
def create_assignment():
    data = request.get_json()

    employee_id = data.get("employee_id")
    job_id = data.get("job_id")

    if not employee_id or not job_id:
        return jsonify({"error": "employee_id and job_id are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # 1. Get dates for the new job
    cur.execute("SELECT start_date, end_date FROM jobs WHERE job_id = %s", (job_id,))
    new_job = cur.fetchone()

    if not new_job:
        return jsonify({"error": "Job not found"}), 404

    new_start = new_job["start_date"]
    new_end = new_job["end_date"]

    # 2. Get all jobs already assigned to employee
    cur.execute("""
        SELECT j.start_date, j.end_date
        FROM assignments a
        JOIN jobs j ON a.job_id = j.job_id
        WHERE a.employee_id = %s
    """, (employee_id,))
    existing = cur.fetchall()

    # 3. Date overlap logic
    for old in existing:
        old_start = old["start_date"]
        old_end = old["end_date"]

        # Overlap check
        if not (new_end < old_start or new_start > old_end):
            return jsonify({"error": "Date overlap detected"}), 409

    # 4. Insert assignment if no overlap
    cur.execute("""
        INSERT INTO assignments (employee_id, job_id)
        VALUES (%s, %s)
    """, (employee_id, job_id))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Assignment created successfully"}), 201

# ------------------------------------------------
# RUN APP
# ------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)