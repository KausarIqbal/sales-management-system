from flask import Flask, jsonify, render_template, request, redirect, session
from werkzeug.middleware.proxy_fix import ProxyFix
from db import get_connection
from psycopg2.extras import RealDictCursor
import os 
print("🔥 NEW CODE DEPLOYED: app.py v3")
app = Flask(__name__)
app.secret_key = "sales_project_secret_2026_hf_fix_12345"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE="None",SESSION_COOKIE_SECURE=True)
@app.route("/ping")
def ping():
    return "pong-v4"
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(
    cursor_factory=RealDictCursor
)

        query = """
        SELECT * FROM employees
        WHERE username=%s
        AND password=%s
        """

        cursor.execute(query, (username, password))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:

            session["user_id"] = user["employee_id"]
            session["role"] = user["role"]
            session["name"] = user["name"]

            return redirect("/dashboard")

        else:

            return "Invalid Username or Password"

    return render_template("login.html")
print("APP LOADED - DEBUG ROUTES ACTIVE")
@app.route("/debug-session")
def debug_session():
    return str(dict(session))

@app.route("/employees")

def employees():

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "manager":
        return "Access Denied"

    conn = get_connection()

    conn = get_connection()
    conn = get_connection()

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = "SELECT * FROM employees"

    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "employees.html",
        employees=data
    )
@app.route("/products")
def products():
    if "user_id" not in session:
        return redirect("/")
    if session["role"] != "manager":
        return "Access Denied"

    conn = get_connection()

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = "SELECT * FROM products"

    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "products.html",
        products=data
    )
@app.route("/add-sale", methods=["GET", "POST"])
def add_sale():

    if "user_id" not in session:
        return redirect("/")

    conn = get_connection()

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Fetch customers
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    # Fetch products
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if request.method == "POST":

        customer_id = request.form["customer_id"]
        product_id = request.form["product_id"]
        quantity = int(request.form["quantity"])

        # Insert into sales table
        sales_query = """
        INSERT INTO sales(employee_id, customer_id, date)
        VALUES(%s, %s, CURRENT_DATE)
        """

        cursor.execute(
            sales_query,
            (session["user_id"], customer_id)
        )

        conn.commit()

        # Get generated sale_id
        sale_id = cursor.lastrowid

        # Get product price
        cursor.execute(
            "SELECT price FROM products WHERE product_id=%s",
            (product_id,)
        )

        product = cursor.fetchone()

        price = product["price"]

        # Insert into sale_items
        sale_item_query = """
        INSERT INTO sale_items(
            sale_id,
            product_id,
            quantity,
            price
        )
        VALUES(%s, %s, %s, %s)
        """

        cursor.execute(
            sale_item_query,
            (sale_id, product_id, quantity, price)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/dashboard")

    return render_template(
        "add_sale.html",
        customers=customers,
        products=products
    )
@app.route("/my-sales")
def my_sales():

    if "user_id" not in session:
        return redirect("/")

    conn = get_connection()

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
    SELECT s.sale_id,
           c.name AS customer,
           s.date,
           SUM(si.quantity * si.price) AS total_amount

    FROM sales s

    JOIN customers c
    ON s.customer_id = c.customer_id

    JOIN sale_items si
    ON s.sale_id = si.sale_id

    WHERE s.employee_id = %s

    GROUP BY s.sale_id,
             c.name,
             s.date
    """

    cursor.execute(query, (session["user_id"],))

    sales = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "my_sales.html",
        sales=sales
    )
@app.route("/my-stock")
def my_stock():

    if "user_id" not in session:
        return redirect("/")

    conn = get_connection()

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """

    SELECT
        p.name AS product_name,
        SUM(sa.quantity_assigned) AS assigned_stock

    FROM stock_assignments sa

    JOIN products p
    ON sa.product_id = p.product_id

    WHERE sa.employee_id = %s

    GROUP BY p.name

    """

    cursor.execute(
        query,
        (session["user_id"],)
    )

    stock = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "my_stock.html",
        stock=stock
    )
@app.route("/customers")
def customers():
    if "user_id" not in session:
        return redirect("/")


    conn = get_connection()

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = "SELECT * FROM customers"

    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(data)
@app.route("/sales-report")
def sales_report():
    if "user_id" not in session:
        return redirect("/")
    if session["role"] != "manager":
        return "Access Denied"



    conn = get_connection()

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
SELECT

    s.sale_id,

    e.name AS sales_rep,

    c.name AS customer,

    p.name AS product,

    si.quantity,

    si.price,

    (si.quantity * si.price) AS total_amount,

    s.date

FROM sales s

JOIN employees e
ON s.employee_id = e.employee_id

JOIN customers c
ON s.customer_id = c.customer_id

JOIN sale_items si
ON s.sale_id = si.sale_id

JOIN products p
ON si.product_id = p.product_id

ORDER BY s.sale_id DESC

"""
    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "sales_report.html",
        sales=data
    )
@app.route("/add-product", methods=["GET", "POST"])
def add_product():

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "manager":
        return "Access Denied"

    if request.method == "POST":

        name = request.form["name"]
        price = request.form["price"]

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO products
        (name, price)
        VALUES (%s,%s)
        """

        cursor.execute(
            query,
            (name, price)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/products")

    return render_template("add_product.html")
@app.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "manager":
        return "Access Denied"

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == "POST":

        name = request.form["name"]
        price = request.form["price"]

        query = """
        UPDATE products
        SET name=%s,
            price=%s
        WHERE product_id=%s
        """

        cursor.execute(
            query,
            (name, price, id)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/products")

    cursor.execute(
        "SELECT * FROM products WHERE product_id=%s",
        (id,)
    )

    product = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "edit_product.html",
        product=product
    )
@app.route("/delete-product/<int:id>")
def delete_product(id):

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "manager":
        return "Access Denied"

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "DELETE FROM products WHERE product_id=%s",
            (id,)
        )

        conn.commit()

    except Exception as e:

        conn.rollback()

        return """
        This product cannot be deleted because
        it is already used in sales records.
        """

    finally:

        cursor.close()
        conn.close()

    return redirect("/products")
@app.route("/add-employee", methods=["GET", "POST"])
def add_employee():

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "manager":
        return "Access Denied"

    conn = get_connection()

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
    SELECT employee_id, name
    FROM employees
    WHERE role = 'manager'
    """)

    managers = cursor.fetchall()

    cursor.close()
    conn.close()

    if request.method == "POST":

        name = request.form["name"]
        role = request.form["role"]
        manager_id = request.form.get("manager_id") or None
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()

        cursor = conn.cursor()

        query = """
        INSERT INTO employees
        (name, role, manager_id, username, password)
        VALUES (%s,%s,%s,%s,%s)
        """

        cursor.execute(
            query,
            (name, role, manager_id, username, password)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/employees")

    return render_template(
        "add_employee.html",
        managers=managers
    )
    
@app.route("/edit-employee/<int:id>", methods=["GET", "POST"])
def edit_employee(id):

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "manager":
        return "Access Denied"

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == "POST":

        name = request.form["name"]
        role = request.form["role"]
        manager_id = request.form.get("manager_id") or None
        username = request.form["username"]
        password = request.form["password"]

        query = """
        UPDATE employees
        SET name=%s,
            role=%s,
            manager_id=%s,
            username=%s,
            password=%s
        WHERE employee_id=%s
        """

        cursor.execute(
            query,
            (name, role,manager_id, username, password, id)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/employees")

    cursor.execute(
        "SELECT * FROM employees WHERE employee_id=%s",
        (id,)
    )

    employee = cursor.fetchone()

    cursor.close()
    conn.close()
    conn = get_connection()

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
    SELECT employee_id, name
    FROM employees
    WHERE role = 'manager'
    """)

    managers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "edit_employee.html",
        employee=employee, managers=managers
    )
@app.route("/delete-employee/<int:id>")
def delete_employee(id):

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "manager":
        return "Access Denied"

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "DELETE FROM employees WHERE employee_id=%s",
            (id,)
        )

        conn.commit()

    except Exception:

        conn.rollback()

        return """
        Cannot delete employee because
        related sales records exist.
        """

    finally:

        cursor.close()
        conn.close()

    return redirect("/employees")
@app.route("/stock-assignment", methods=["GET", "POST"])
def stock_assignment():

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "manager":
        return "Access Denied"

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Save Assignment

    if request.method == "POST":

        employee_id = request.form["employee_id"]
        product_id = request.form["product_id"]
        quantity = request.form["quantity"]

        query = """
        INSERT INTO stock_assignments
        (employee_id, product_id, quantity_assigned, date)
        VALUES (%s,%s,%s,CURRENT_DATE)
        """

        cursor.execute(
            query,
            (employee_id, product_id, quantity)
        )

        conn.commit()

    # Sales Reps Dropdown

    cursor.execute("""
    SELECT employee_id, name
    FROM employees
    WHERE role='sales_rep'
    """)

    employees = cursor.fetchall()

    # Products Dropdown

    cursor.execute("""
    SELECT product_id, name
    FROM products
    """)

    products = cursor.fetchall()

    # Assignment History

    cursor.execute("""

    SELECT
        sa.assignment_id,
        e.name AS employee_name,
        p.name AS product_name,
        sa.quantity_assigned,
        sa.date

    FROM stock_assignments sa

    JOIN employees e
    ON sa.employee_id = e.employee_id

    JOIN products p
    ON sa.product_id = p.product_id

    ORDER BY sa.assignment_id DESC

    """)

    assignments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "stock_assignment.html",
        employees=employees,
        products=products,
        assignments=assignments
    )
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # =========================
    # MANAGER DASHBOARD
    # =========================

    if session["role"] == "manager":

        # Total Employees
        cursor.execute("SELECT COUNT(*) AS total FROM employees")
        total_employees = cursor.fetchone()['total']

        # Total Products
        cursor.execute("SELECT COUNT(*) AS total FROM products")
        total_products = cursor.fetchone()['total']

        # Total Sales
        cursor.execute("SELECT COUNT(*) AS total FROM sales")
        total_sales = cursor.fetchone()['total']

        # Total Revenue
        cursor.execute("""
            SELECT COALESCE(SUM(quantity * price),0) AS revenue
            FROM sale_items
        """)
        total_revenue = cursor.fetchone()['revenue']

        # Top Sales Rep
        cursor.execute("""
        SELECT e.name,
               SUM(si.quantity * si.price) AS total_sales
        FROM sales s
        JOIN employees e
        ON s.employee_id = e.employee_id
        JOIN sale_items si
        ON s.sale_id = si.sale_id
        GROUP BY e.name
        ORDER BY total_sales DESC
        LIMIT 1
        """)
        top_rep = cursor.fetchone()

        # Top Product
        cursor.execute("""
        SELECT p.name,
               SUM(si.quantity) AS total_sold
        FROM sale_items si
        JOIN products p
        ON si.product_id = p.product_id
        GROUP BY p.name
        ORDER BY total_sold DESC
        LIMIT 1
        """)
        top_product = cursor.fetchone()

        # Top Customer
        cursor.execute("""
        SELECT c.name,
               COUNT(s.sale_id) AS total_orders
        FROM sales s
        JOIN customers c
        ON s.customer_id = c.customer_id
        GROUP BY c.name
        ORDER BY total_orders DESC
        LIMIT 1
        """)
        top_customer = cursor.fetchone()

        # Remaining Stock
        cursor.execute("""
        SELECT e.name,

               COALESCE(SUM(sa.quantity_assigned),0)
               -
               COALESCE(SUM(si.quantity),0)

               AS remaining_stock

        FROM employees e

        LEFT JOIN stock_assignments sa
        ON e.employee_id = sa.employee_id

        LEFT JOIN sales s
        ON e.employee_id = s.employee_id

        LEFT JOIN sale_items si
        ON s.sale_id = si.sale_id

        GROUP BY e.name
        """)

        remaining_stock = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            "dashboard.html",
            total_employees=total_employees,
            total_products=total_products,
            total_sales=total_sales,
            total_revenue=total_revenue,
            top_rep=top_rep,
            top_customer=top_customer,
            top_product=top_product,
            remaining_stock=remaining_stock
        )

    # =========================
    # SALES REP DASHBOARD
    # =========================

    else:

        # My Sales Count
        cursor.execute("""
        SELECT COUNT(*) AS total_sales
        FROM sales
        WHERE employee_id = %s
        """, (session["user_id"],))

        my_sales = cursor.fetchone()["total_sales"]

        # My Revenue
        cursor.execute("""
        SELECT COALESCE(
            SUM(si.quantity * si.price),0
        ) AS revenue

        FROM sales s

        JOIN sale_items si
        ON s.sale_id = si.sale_id

        WHERE s.employee_id = %s
        """, (session["user_id"],))

        my_revenue = cursor.fetchone()["revenue"]

        # My Customers
        cursor.execute("""
        SELECT COUNT(DISTINCT customer_id)
        AS customers

        FROM sales

        WHERE employee_id = %s
        """, (session["user_id"],))

        my_customers = cursor.fetchone()["customers"]

        cursor.close()
        conn.close()

        return render_template(
            "sales_dashboard.html",
            my_sales=my_sales,
            my_revenue=my_revenue,
            my_customers=my_customers
        )

    
    
    
    

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
