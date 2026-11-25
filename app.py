
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Database connection
def get_db():
    conn = sqlite3.connect("employees.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create employee table
with get_db() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            salary REAL NOT NULL
        )
    """)

# Home page - View and Search
@app.route("/")
def index():
    search = request.args.get("search", "")

    conn = get_db()

    employees = conn.execute("""
        SELECT * FROM employees
        WHERE CAST(id AS TEXT) LIKE ?
        OR name LIKE ?
        ORDER BY id
    """, ('%' + search + '%', '%' + search + '%')).fetchall()

    conn.close()

    return render_template("index.html", employees=employees)

# Add employee
@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    email = request.form["email"]
    department = request.form["department"]
    salary = request.form["salary"]

    with get_db() as conn:
        conn.execute("""
            INSERT INTO employees
            (name, email, department, salary)
            VALUES (?, ?, ?, ?)
        """, (name, email, department, salary))

    return redirect("/")

# Update employee
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    conn = get_db()

    if request.method == "POST":
        conn.execute("""
            UPDATE employees
            SET name=?, email=?, department=?, salary=?
            WHERE id=?
        """, (
            request.form["name"],
            request.form["email"],
            request.form["department"],
            request.form["salary"],
            id
        ))

        conn.close()
        return redirect("/")

    employee = conn.execute(
        "SELECT * FROM employees WHERE id=?", (id,)
    ).fetchone()

    conn.close()

    if employee is None:
        return "Employee not found", 404

    return render_template("update.html", employee=employee)

# Delete employee
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM employees WHERE id=?", (id,)
        )

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
