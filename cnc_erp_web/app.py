from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
from datetime import datetime
from fpdf import FPDF
import os

app = Flask(__name__)
app.config['DATABASE'] = 'instance/erp.sqlite3'
app.config['UPLOAD_FOLDER'] = 'quotes'

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    conn = get_db_connection()
    jobs = conn.execute('SELECT * FROM jobs ORDER BY due_date ASC').fetchall()
    conn.close()
    return render_template('dashboard.html', jobs=jobs)

@app.route('/customers')
def customers():
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers').fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)

@app.route('/customers/new', methods=['GET', 'POST'])
def new_customer():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        conn = get_db_connection()
        conn.execute('INSERT INTO customers (name, contact, email, phone, address) VALUES (?, ?, ?, ?, ?)',
                     (name, contact, email, phone, address))
        conn.commit()
        conn.close()
        return redirect(url_for('customers'))
    return render_template('new_customer.html')

@app.route('/jobs/new', methods=['GET', 'POST'])
def new_job():
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers').fetchall()
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        description = request.form['description']
        due_date = request.form['due_date']
        status = 'Quoted'
        conn.execute('INSERT INTO jobs (customer_id, description, due_date, status) VALUES (?, ?, ?, ?)',
                     (customer_id, description, due_date, status))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('new_job.html', customers=customers)

@app.route('/quotes/new/<int:job_id>', methods=['GET', 'POST'])
def new_quote(job_id):
    conn = get_db_connection()
    job = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    customer = conn.execute('SELECT * FROM customers WHERE id = ?', (job['customer_id'],)).fetchone()
    if request.method == 'POST':
        rate = float(request.form['hourly_rate'])
        hours = float(request.form['estimated_hours'])
        material = float(request.form['material_cost'])
        markup = float(request.form['markup'])
        subtotal = (rate * hours + material)
        total = subtotal * (1 + markup / 100)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"quote_{job_id}.pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Quote for Job #{job_id}", ln=True)
        pdf.cell(200, 10, txt=f"Customer: {customer['name']}", ln=True)
        pdf.cell(200, 10, txt=f"Description: {job['description']}", ln=True)
        pdf.cell(200, 10, txt=f"Rate: ${rate:.2f}/hr", ln=True)
        pdf.cell(200, 10, txt=f"Estimated Hours: {hours}", ln=True)
        pdf.cell(200, 10, txt=f"Material Cost: ${material:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Markup: {markup}%", ln=True)
        pdf.cell(200, 10, txt=f"Total Price: ${total:.2f}", ln=True)
        pdf.output(pdf_path)
        conn.execute('INSERT INTO quotes (job_id, date_created, hourly_rate, estimated_hours, material_cost, markup_percent, total_price, pdf_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                     (job_id, datetime.now().isoformat(), rate, hours, material, markup, total, pdf_path))
        conn.commit()
        conn.close()
        return redirect(url_for('download_quote', job_id=job_id))
    return render_template('new_quote.html', job=job, customer=customer)

@app.route('/quotes/<int:job_id>/download')
def download_quote(job_id):
    conn = get_db_connection()
    quote = conn.execute('SELECT * FROM quotes WHERE job_id = ?', (job_id,)).fetchone()
    conn.close()
    return send_file(quote['pdf_path'], as_attachment=True)

if __name__ == '__main__':
    os.makedirs('quotes', exist_ok=True)
    os.makedirs('instance', exist_ok=True)
    app.run(debug=True)
