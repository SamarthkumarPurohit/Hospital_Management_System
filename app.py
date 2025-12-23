from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)
DB = "hospital.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        contact TEXT,
        disease TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        doctor TEXT,
        date TEXT,
        time TEXT,
        status TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS medicines(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        quantity INTEGER,
        price REAL,
        expiry TEXT,
        manufacturer TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS billing(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        items TEXT,
        amount INTEGER,
        bill_date TEXT,
        status TEXT
    )""")

    db.commit()
    db.close()

# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():
    db = get_db()

    total_patients = db.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    total_appointments = db.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    total_medicines = db.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]
    pending_bills = db.execute("SELECT COUNT(*) FROM billing WHERE status='Pending'").fetchone()[0]
    total_revenue = db.execute(
        "SELECT IFNULL(SUM(amount),0) FROM billing WHERE status='Paid'"
    ).fetchone()[0]

    recent_appointments = db.execute(
        "SELECT * FROM appointments ORDER BY id DESC LIMIT 5"
    ).fetchall()

    db.close()

    return render_template(
        "dashboard.html",
        total_patients=total_patients,
        total_appointments=total_appointments,
        total_medicines=total_medicines,
        pending_bills=pending_bills,
        total_revenue=total_revenue,
        recent_appointments=recent_appointments
    )

# ---------------- PATIENTS ----------------
@app.route("/patients", methods=["GET","POST"])
def patients():
    db = get_db()
    if request.method == "POST":
        db.execute(
            "INSERT INTO patients VALUES(NULL,?,?,?,?,?)",
            (
                request.form["name"],
                request.form["age"],
                request.form["gender"],
                request.form["contact"],
                request.form["disease"]
            )
        )
        db.commit()
        return redirect("/patients")

    data = db.execute("SELECT * FROM patients").fetchall()
    db.close()
    return render_template("patients.html", patients=data)

@app.route("/edit_patient/<int:id>", methods=["GET","POST"])
def edit_patient(id):
    db = get_db()
    if request.method == "POST":
        db.execute(
            """UPDATE patients
               SET name=?, age=?, gender=?, contact=?, disease=?
               WHERE id=?""",
            (
                request.form["name"],
                request.form["age"],
                request.form["gender"],
                request.form["contact"],
                request.form["disease"],
                id
            )
        )
        db.commit()
        return redirect("/patients")

    patient = db.execute("SELECT * FROM patients WHERE id=?", (id,)).fetchone()
    db.close()
    return render_template("edit_patient.html", patient=patient)

# ---------------- APPOINTMENTS ----------------
@app.route("/appointments", methods=["GET","POST"])
def appointments():
    db = get_db()
    if request.method == "POST":
        db.execute(
            "INSERT INTO appointments VALUES(NULL,?,?,?,?,?)",
            (
                request.form["patient_name"],
                request.form["doctor"],
                request.form["date"],
                request.form["time"],
                "Scheduled"
            )
        )
        db.commit()
        return redirect("/appointments")

    data = db.execute("SELECT * FROM appointments").fetchall()
    db.close()
    return render_template("appointments.html", appointments=data)

@app.route("/edit_appointment/<int:id>", methods=["GET","POST"])
def edit_appointment(id):
    db = get_db()
    if request.method == "POST":
        db.execute(
            """UPDATE appointments
               SET patient_name=?, doctor=?, date=?, time=?, status=?
               WHERE id=?""",
            (
                request.form["patient_name"],
                request.form["doctor"],
                request.form["date"],
                request.form["time"],
                request.form["status"],
                id
            )
        )
        db.commit()
        return redirect("/appointments")

    appt = db.execute("SELECT * FROM appointments WHERE id=?", (id,)).fetchone()
    db.close()
    return render_template("edit_appointment.html", appt=appt)

# ---------------- MEDICINES ----------------
@app.route("/medicines", methods=["GET","POST"])
def medicines():
    db = get_db()
    if request.method == "POST":
        db.execute(
            "INSERT INTO medicines VALUES(NULL,?,?,?,?,?,?)",
            (
                request.form["name"],
                request.form["category"],
                request.form["quantity"],
                request.form["price"],
                request.form["expiry"],
                request.form["manufacturer"]
            )
        )
        db.commit()
        return redirect("/medicines")

    meds = db.execute("SELECT * FROM medicines").fetchall()
    db.close()
    return render_template("medicines.html", medicines=meds)

@app.route("/edit_medicine/<int:id>", methods=["GET","POST"])
def edit_medicine(id):
    db = get_db()
    if request.method == "POST":
        db.execute(
            """UPDATE medicines
               SET name=?, category=?, quantity=?, price=?, expiry=?, manufacturer=?
               WHERE id=?""",
            (
                request.form["name"],
                request.form["category"],
                request.form["quantity"],
                request.form["price"],
                request.form["expiry"],
                request.form["manufacturer"],
                id
            )
        )
        db.commit()
        return redirect("/medicines")

    med = db.execute("SELECT * FROM medicines WHERE id=?", (id,)).fetchone()
    db.close()
    return render_template("edit_medicine.html", med=med)

# ---------------- BILLING ----------------
@app.route("/billing", methods=["GET","POST"])
def billing():
    db = get_db()
    if request.method == "POST":
        db.execute(
            "INSERT INTO billing VALUES(NULL,?,?,?,?,?)",
            (
                request.form["patient_name"],
                request.form["items"],
                request.form["amount"],
                str(date.today()),
                request.form["status"]
            )
        )
        db.commit()
        return redirect("/billing")

    bills = db.execute("SELECT * FROM billing").fetchall()
    db.close()
    return render_template("billing.html", bills=bills)

@app.route("/edit_bill/<int:id>", methods=["GET","POST"])
def edit_bill(id):
    db = get_db()
    if request.method == "POST":
        db.execute(
            """UPDATE billing
               SET patient_name=?, items=?, amount=?, status=?
               WHERE id=?""",
            (
                request.form["patient_name"],
                request.form["items"],
                request.form["amount"],
                request.form["status"],
                id
            )
        )
        db.commit()
        return redirect("/billing")

    bill = db.execute("SELECT * FROM billing WHERE id=?", (id,)).fetchone()
    db.close()
    return render_template("edit_bill.html", bill=bill)

# ---------------- RUN ----------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
