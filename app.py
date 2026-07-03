<<<<<<< HEAD
from flask import Flask, render_template, request, send_file, redirect
import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import os

app = Flask(__name__)


# ---------------- DATABASE ----------------

def create_tables():

    conn = sqlite3.connect("food_data.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        students INTEGER,
        rice REAL,
        curry REAL,
        chapati INTEGER,
        dal REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        feedback TEXT
    )
    """)

    conn.commit()
    conn.close()


create_tables()


# ---------------- HOME ----------------

@app.route('/')
def home():
    return render_template('index.html')


# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    students = 70
    rice = students * 0.4
    curry = students * 0.25
    waste = 2
    savings = 4000

    return render_template(
        'dashboard.html',
        students=students,
        rice=rice,
        curry=curry,
        waste=waste,
        savings=savings
    )


# ---------------- FOOD PREDICTION ----------------

@app.route('/predict', methods=['GET', 'POST'])
def predict():

    prediction = None

    if request.method == 'POST':

        students = int(request.form['students'])

        rice = students * 0.4
        curry = students * 0.25
        chapati = students * 3
        dal = students * 0.15

        prediction = (
            f"Rice : {rice:.1f} Kg | "
            f"Curry : {curry:.1f} Kg | "
            f"Chapati : {chapati} | "
            f"Dal : {dal:.1f} Kg"
        )

        conn = sqlite3.connect("food_data.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO predictions
        (students,rice,curry,chapati,dal)
        VALUES(?,?,?,?,?)
        """, (students, rice, curry, chapati, dal))

        conn.commit()
        conn.close()

    return render_template(
        "predict.html",
        prediction=prediction
    )
# ---------------- FOOD WASTE CALCULATOR ----------------

@app.route('/waste', methods=['GET', 'POST'])
def waste():

    waste = None

    if request.method == 'POST':

        prepared = float(request.form['prepared'])
        consumed = float(request.form['consumed'])

        waste = prepared - consumed

    return render_template(
        'waste.html',
        waste=waste
    )


# ---------------- DAILY REPORT ----------------

@app.route('/report')
def report():
    return render_template('report.html')


# ---------------- FOOD WASTE CHART ----------------

@app.route('/chart')
def chart():

    labels = ['Food Consumed', 'Food Wasted']
    values = [90, 10]

    plt.figure(figsize=(6, 6))
    plt.pie(values,
            labels=labels,
            autopct='%1.1f%%')

    plt.title("Food Waste Analysis")

    if not os.path.exists("static"):
        os.makedirs("static")

    plt.savefig("static/chart.png")
    plt.close()

    return render_template("chart.html")


# ---------------- ADMIN LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    message = ""

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            message = "Login Successful!"
        else:
            message = "Invalid Username or Password"

    return render_template(
        'login.html',
        message=message
    )


# ---------------- USER REGISTRATION ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    message = ""

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("food_data.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users(username,password)
        VALUES(?,?)
        """, (username, password))

        conn.commit()
        conn.close()

        message = "Registration Successful!"

    return render_template(
        'register.html',
        message=message
    )
# ---------------- FEEDBACK ----------------

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():

    message = ""

    if request.method == "POST":

        username = request.form['username']
        feedback_text = request.form['feedback']

        conn = sqlite3.connect("food_data.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO feedback(username,feedback)
        VALUES(?,?)
        """, (username, feedback_text))

        conn.commit()
        conn.close()

        message = "Feedback Submitted Successfully!"

    return render_template(
        "feedback.html",
        message=message
    )


# ---------------- CONTACT ----------------

@app.route('/contact')
def contact():
    return render_template("contact.html")


# ---------------- ABOUT ----------------

@app.route('/about')
def about():
    return render_template("about.html")


# ---------------- HISTORY ----------------

@app.route('/history', methods=['GET', 'POST'])
def history():

    conn = sqlite3.connect("food_data.db")
    cursor = conn.cursor()

    search = ""

    if request.method == "POST":

        search = request.form['search']

        cursor.execute("""
        SELECT id,
               students,
               rice,
               curry,
               chapati,
               dal
        FROM predictions
        WHERE students LIKE ?
        ORDER BY id DESC
        """, ('%' + search + '%',))

    else:

        cursor.execute("""
        SELECT id,
               students,
               rice,
               curry,
               chapati,
               dal
        FROM predictions
        ORDER BY id DESC
        """)

    rows = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        rows=rows,
        search=search
    )


# ---------------- DELETE HISTORY ----------------

@app.route('/delete/<int:id>')
def delete(id):

    conn = sqlite3.connect("food_data.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM predictions WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/history")
# ---------------- DOWNLOAD PDF REPORT ----------------

@app.route('/download_report')
def download_report():

    pdf = canvas.Canvas("Food_Report.pdf")

    pdf.setTitle("Food Waste Report")

    pdf.drawString(100, 800, "Smart Hostel Food Management")
    pdf.drawString(100, 780, "Food Waste Reduction Report")

    pdf.drawString(100, 740, "Students Present : 70")
    pdf.drawString(100, 720, "Rice Required : 28 Kg")
    pdf.drawString(100, 700, "Curry Required : 17.5 Kg")
    pdf.drawString(100, 680, "Food Waste : 2 Kg")
    pdf.drawString(100, 660, "Monthly Savings : Rs.4000")

    pdf.save()

    return send_file(
        "Food_Report.pdf",
        as_attachment=True
    )


# ---------------- MACHINE LEARNING PREDICTION ----------------

@app.route('/ml_predict')
def ml_predict():

    try:

        data = pd.read_csv("food_waste.csv")

        data["day_num"] = range(1, len(data) + 1)

        X = data[["day_num"]]
        y = data["students"]

        model = LinearRegression()
        model.fit(X, y)

        next_day = [[len(data) + 1]]

        predicted_students = int(model.predict(next_day)[0])

    except Exception:

        predicted_students = 70

    return render_template(
        "ml_predict.html",
        predicted_students=predicted_students
    )


# ---------------- ATTENDANCE ----------------

@app.route('/attendance')
def attendance():
    return render_template("attendance.html")


# ---------------- FOOD DONATION ----------------

@app.route('/donation')
def donation():
    return render_template("donation.html")
# ---------------- INVENTORY ----------------

@app.route('/inventory')
def inventory():

    items = [
        ("Rice", "150 Kg"),
        ("Dal", "50 Kg"),
        ("Vegetables", "80 Kg"),
        ("Cooking Oil", "25 L"),
        ("Spices", "15 Kg")
    ]

    return render_template(
        "inventory.html",
        items=items
    )


# ---------------- EXPENSE ----------------

@app.route('/expense')
def expense():

    total_expense = 25000
    monthly_savings = 4000

    return render_template(
        "expense.html",
        expense=total_expense,
        savings=monthly_savings
    )


# ---------------- ADMIN PANEL ----------------

@app.route('/admin')
def admin():

    conn = sqlite3.connect("food_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback")
    total_feedback = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        users=total_users,
        predictions=total_predictions,
        feedback=total_feedback
    )


# ---------------- EXPORT HISTORY TO EXCEL ----------------

@app.route('/export_excel')
def export_excel():

    conn = sqlite3.connect("food_data.db")

    df = pd.read_sql_query(
        "SELECT * FROM predictions",
        conn
    )

    conn.close()

    file_name = "Prediction_History.xlsx"

    df.to_excel(file_name, index=False)

    return send_file(
        file_name,
        as_attachment=True
    )


# ---------------- ERROR PAGE ----------------

@app.errorhandler(404)
def page_not_found(error):

    return (
        "<h2>404 - Page Not Found</h2>"
        "<a href='/'>Go Home</a>",
        404
    )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    create_tables()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
=======
from flask import Flask, render_template, request, send_file, redirect
import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import os

app = Flask(__name__)


# ---------------- DATABASE ----------------

def create_tables():

    conn = sqlite3.connect("food_data.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        students INTEGER,
        rice REAL,
        curry REAL,
        chapati INTEGER,
        dal REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        feedback TEXT
    )
    """)

    conn.commit()
    conn.close()


create_tables()


# ---------------- HOME ----------------

@app.route('/')
def home():
    return render_template('index.html')


# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    students = 70
    rice = students * 0.4
    curry = students * 0.25
    waste = 2
    savings = 4000

    return render_template(
        'dashboard.html',
        students=students,
        rice=rice,
        curry=curry,
        waste=waste,
        savings=savings
    )


# ---------------- FOOD PREDICTION ----------------

@app.route('/predict', methods=['GET', 'POST'])
def predict():

    prediction = None

    if request.method == 'POST':

        students = int(request.form['students'])

        rice = students * 0.4
        curry = students * 0.25
        chapati = students * 3
        dal = students * 0.15

        prediction = (
            f"Rice : {rice:.1f} Kg | "
            f"Curry : {curry:.1f} Kg | "
            f"Chapati : {chapati} | "
            f"Dal : {dal:.1f} Kg"
        )

        conn = sqlite3.connect("food_data.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO predictions
        (students,rice,curry,chapati,dal)
        VALUES(?,?,?,?,?)
        """, (students, rice, curry, chapati, dal))

        conn.commit()
        conn.close()

    return render_template(
        "predict.html",
        prediction=prediction
    )
# ---------------- FOOD WASTE CALCULATOR ----------------

@app.route('/waste', methods=['GET', 'POST'])
def waste():

    waste = None

    if request.method == 'POST':

        prepared = float(request.form['prepared'])
        consumed = float(request.form['consumed'])

        waste = prepared - consumed

    return render_template(
        'waste.html',
        waste=waste
    )


# ---------------- DAILY REPORT ----------------

@app.route('/report')
def report():
    return render_template('report.html')


# ---------------- FOOD WASTE CHART ----------------

@app.route('/chart')
def chart():

    labels = ['Food Consumed', 'Food Wasted']
    values = [90, 10]

    plt.figure(figsize=(6, 6))
    plt.pie(values,
            labels=labels,
            autopct='%1.1f%%')

    plt.title("Food Waste Analysis")

    if not os.path.exists("static"):
        os.makedirs("static")

    plt.savefig("static/chart.png")
    plt.close()

    return render_template("chart.html")


# ---------------- ADMIN LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    message = ""

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            message = "Login Successful!"
        else:
            message = "Invalid Username or Password"

    return render_template(
        'login.html',
        message=message
    )


# ---------------- USER REGISTRATION ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    message = ""

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("food_data.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users(username,password)
        VALUES(?,?)
        """, (username, password))

        conn.commit()
        conn.close()

        message = "Registration Successful!"

    return render_template(
        'register.html',
        message=message
    )
# ---------------- FEEDBACK ----------------

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():

    message = ""

    if request.method == "POST":

        username = request.form['username']
        feedback_text = request.form['feedback']

        conn = sqlite3.connect("food_data.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO feedback(username,feedback)
        VALUES(?,?)
        """, (username, feedback_text))

        conn.commit()
        conn.close()

        message = "Feedback Submitted Successfully!"

    return render_template(
        "feedback.html",
        message=message
    )


# ---------------- CONTACT ----------------

@app.route('/contact')
def contact():
    return render_template("contact.html")


# ---------------- ABOUT ----------------

@app.route('/about')
def about():
    return render_template("about.html")


# ---------------- HISTORY ----------------

@app.route('/history', methods=['GET', 'POST'])
def history():

    conn = sqlite3.connect("food_data.db")
    cursor = conn.cursor()

    search = ""

    if request.method == "POST":

        search = request.form['search']

        cursor.execute("""
        SELECT id,
               students,
               rice,
               curry,
               chapati,
               dal
        FROM predictions
        WHERE students LIKE ?
        ORDER BY id DESC
        """, ('%' + search + '%',))

    else:

        cursor.execute("""
        SELECT id,
               students,
               rice,
               curry,
               chapati,
               dal
        FROM predictions
        ORDER BY id DESC
        """)

    rows = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        rows=rows,
        search=search
    )


# ---------------- DELETE HISTORY ----------------

@app.route('/delete/<int:id>')
def delete(id):

    conn = sqlite3.connect("food_data.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM predictions WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/history")
# ---------------- DOWNLOAD PDF REPORT ----------------

@app.route('/download_report')
def download_report():

    pdf = canvas.Canvas("Food_Report.pdf")

    pdf.setTitle("Food Waste Report")

    pdf.drawString(100, 800, "Smart Hostel Food Management")
    pdf.drawString(100, 780, "Food Waste Reduction Report")

    pdf.drawString(100, 740, "Students Present : 70")
    pdf.drawString(100, 720, "Rice Required : 28 Kg")
    pdf.drawString(100, 700, "Curry Required : 17.5 Kg")
    pdf.drawString(100, 680, "Food Waste : 2 Kg")
    pdf.drawString(100, 660, "Monthly Savings : Rs.4000")

    pdf.save()

    return send_file(
        "Food_Report.pdf",
        as_attachment=True
    )


# ---------------- MACHINE LEARNING PREDICTION ----------------

@app.route('/ml_predict')
def ml_predict():

    try:

        data = pd.read_csv("food_waste.csv")

        data["day_num"] = range(1, len(data) + 1)

        X = data[["day_num"]]
        y = data["students"]

        model = LinearRegression()
        model.fit(X, y)

        next_day = [[len(data) + 1]]

        predicted_students = int(model.predict(next_day)[0])

    except Exception:

        predicted_students = 70

    return render_template(
        "ml_predict.html",
        predicted_students=predicted_students
    )


# ---------------- ATTENDANCE ----------------

@app.route('/attendance')
def attendance():
    return render_template("attendance.html")


# ---------------- FOOD DONATION ----------------

@app.route('/donation')
def donation():
    return render_template("donation.html")
# ---------------- INVENTORY ----------------

@app.route('/inventory')
def inventory():

    items = [
        ("Rice", "150 Kg"),
        ("Dal", "50 Kg"),
        ("Vegetables", "80 Kg"),
        ("Cooking Oil", "25 L"),
        ("Spices", "15 Kg")
    ]

    return render_template(
        "inventory.html",
        items=items
    )


# ---------------- EXPENSE ----------------

@app.route('/expense')
def expense():

    total_expense = 25000
    monthly_savings = 4000

    return render_template(
        "expense.html",
        expense=total_expense,
        savings=monthly_savings
    )


# ---------------- ADMIN PANEL ----------------

@app.route('/admin')
def admin():

    conn = sqlite3.connect("food_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback")
    total_feedback = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        users=total_users,
        predictions=total_predictions,
        feedback=total_feedback
    )


# ---------------- EXPORT HISTORY TO EXCEL ----------------

@app.route('/export_excel')
def export_excel():

    conn = sqlite3.connect("food_data.db")

    df = pd.read_sql_query(
        "SELECT * FROM predictions",
        conn
    )

    conn.close()

    file_name = "Prediction_History.xlsx"

    df.to_excel(file_name, index=False)

    return send_file(
        file_name,
        as_attachment=True
    )


# ---------------- ERROR PAGE ----------------

@app.errorhandler(404)
def page_not_found(error):

    return (
        "<h2>404 - Page Not Found</h2>"
        "<a href='/'>Go Home</a>",
        404
    )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    create_tables()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
>>>>>>> a83d3ec77f5db0e2315dd4870fbf59a1e381cd4b
    )