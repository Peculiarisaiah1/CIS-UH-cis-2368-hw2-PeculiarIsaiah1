from flask import Flask, request, jsonify
import mysql.connector
import os

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
# ROUTE: GET ALL TICKETS
# ------------------------------------------------
@app.route("/tickets", methods=["GET"])
def get_all_tickets():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM tickets")
    result = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(result), 200

# ------------------------------------------------
# ROUTE: GET TICKET BY NUMBER
# ------------------------------------------------
@app.route("/tickets/<int:ticketno>", methods=["GET"])
def get_ticket(ticketno):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM tickets WHERE ticketno = %s", (ticketno,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:
        return jsonify(result), 200
    else:
        return jsonify({"error": "Ticket not found"}), 404

# ------------------------------------------------
# ROUTE: CREATE PERSON
# ------------------------------------------------
@app.route("/person", methods=["POST"])
def create_person():
    data = request.get_json()

    firstname = data.get("firstname")
    lastname = data.get("lastname")

    conn = get_db_connection()
    cur = conn.cursor()

    sql = "INSERT INTO person (firstname, lastname) VALUES (%s, %s)"
    val = (firstname, lastname)

    cur.execute(sql, val)
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "Person created successfully"}), 201

# ------------------------------------------------
# ROUTE: REASSIGN JOB (OPTIONAL FOR HW)
# ------------------------------------------------
@app.route("/reassign/<int:job_id>", methods=["PUT"])
def reassign_job(job_id):
    conn = get_db_connection()
    cur = conn.cursor()

    sql = "UPDATE jobs SET assigned = 'Yes' WHERE job_id = %s"
    cur.execute(sql, (job_id,))
    conn.commit()

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        return jsonify({"error": "Job not found"}), 404

    cur.close()
    conn.close()

    return jsonify({"message": "Reassigned successfully"}), 200

# ------------------------------------------------
# RUN APP
# ------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)