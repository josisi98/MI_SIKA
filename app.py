from flask import Flask, request, flash, redirect, url_for, render_template, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'lavienestrien'

# Routes
@app.route('/')
def accueil():
    return render_template('Accueil.html', title='Accueil')

@app.route('/apropos')
def apropos():
    return render_template('Apropos.html', title='À propos')

@app.route('/simulateur')
def simulateur():
    return render_template('Simulateur.html', title='Simulateur')

# adresse e-mail réelle
receiving_email_address = 'josiaskouassi98@gmail.com'
# Configuration du serveur SMTP (remplacez par vos propres informations)
smtp_host = 'smtp.example.com'
smtp_port = 587
smtp_username = 'Tayler'
smtp_password = 'verlaine@12'


def send_email(name, email, subject, message):
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = receiving_email_address
    msg['Subject'] = subject

    # Corps du message
    body = f"Nom : {name}\nEmail : {email}\nMessage :\n{message}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(email, receiving_email_address, msg.as_string())
            return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    if send_email(name, email, subject, message):
        flash('Votre message a été envoyé. Merci!', 'success')
    else:
        flash('Erreur lors de l\'envoi de l\'e-mail.', 'danger')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)