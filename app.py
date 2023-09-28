from flask import Flask, request, flash, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'lavienestrien'

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MI_SIKA.db'
db = SQLAlchemy(app)

# Modèle Utilisateur
class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    messages = db.relationship('Message', backref='expediteur', lazy=True)

    def __repr__(self):
        return f'Utilisateur({self.nom}, {self.email})'

# Modèle Message
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sujet = db.Column(db.String(200), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    expediteur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)

    def __repr__(self):
        return f'Message({self.sujet}, {self.expediteur_id})'

# Configuration du serveur SMTP (remplacez par vos propres informations)
receiving_email_address = 'josiaskouassi98@gmail.com'
smtp_host = 'smtp.example.com'
smtp_port = 587
smtp_username = 'Tayler'
smtp_password = 'verlaine@12'

# Fonction d'envoi d'e-mail (inchangée)
def send_email(name, email, subject, message):
    sender_email = 'votre_adresse@gmail.com'  # Remplacez par votre adresse e-mail

    # Configuration du serveur SMTP
    smtp_host = 'smtp.gmail.com'  # Serveur SMTP de Gmail
    smtp_port = 587  # Port SMTP de Gmail
    smtp_username = 'votre_adresse@gmail.com'  # Remplacez par votre adresse e-mail Gmail
    smtp_password = 'votre_mot_de_passe'  # Remplacez par votre mot de passe Gmail

    # Création de l'objet e-mail
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    # Corps du message
    body = f"Nom : {name}\nEmail : {email}\nMessage :\n{message}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connexion au serveur SMTP
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            # Login avec votre compte SMTP
            server.login(smtp_username, smtp_password)
            # Envoi de l'e-mail
            server.sendmail(sender_email, email, msg.as_string())
            return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {str(e)}")
        return False

# Exemple d'utilisation
send_email('John Doe', 'john.doe@example.com', 'Test', 'Ceci est un message de test.')

# Routes (avec modification de l'ancienne route '/')
@app.route('/')
def accueil():
    return render_template('Accueil.html', title='Accueil')

@app.route('/apropos')
def apropos():
    return render_template('Apropos.html', title='À propos')

@app.route('/simulateur')
def simulateur():
    return render_template('Simulateur.html', title='Simulateur')

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

    return redirect(url_for('accueil'))

if __name__ == '__main__':
    db.create_all()  # Crée les tables avant de lancer l'application
    app.run(debug=True)
