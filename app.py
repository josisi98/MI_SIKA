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
    
    # Modèle de données pour chaque étape du formulaire
class Etape(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    statut_professionnel = db.Column(db.String(50))
    revenus_annuels_2023 = db.Column(db.Float)
    progression_annuelle = db.Column(db.Integer)
    age = db.Column(db.Integer)
    mode_versements = db.Column(db.String(10))
    versements_annee = db.Column(db.Float)
    versements_proportionnels = db.Column(db.Float)
    age_retraite = db.Column(db.Integer)
    versements_fixes = db.Column(db.Float)
    progression_annuelle_revenus = db.Column(db.Integer)


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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Récupérer les données du formulaire et enregistrer dans la base de données
        etape = Etape(
            statut_professionnel=request.form.get('STAT_PRO'),
            revenus_annuels_2023=float(request.form.get('REV_0', 0)),
            progression_annuelle=int(request.form.get('TX_AUG_SAL', 0)),
            age=int(request.form.get('AGE_0', 0)),
            mode_versements=request.form.get('MOD_VERS', ''),
            versements_annee=float(request.form.get('VERS_0', 0)),
            versements_proportionnels=float(request.form.get('PERC_SAL', 0)),
            age_retraite=int(request.form.get('AGE_END', 0)),
            versements_fixes=float(request.form.get('VERS_ANN', 0)),
            progression_annuelle_revenus=int(request.form.get('TX_AUG_SAL', 0))
        )
        db.session.add(etape)
        db.session.commit()
        
        # Rediriger vers l'étape suivante
        return redirect(url_for('etape_suivante'))

    return render_template('index.html')
@app.route('/simulation', methods=['POST'])
def simulation():
    # Récupérer les données du formulaire
    age_actuel = int(request.form.get('AGE_0', 0))
    age_retraite = int(request.form.get('AGE_END', 0))
    mode_versements = request.form.get('MOD_VERS')

    # Initialiser les variables de simulation
    annees_jusqu_retraite = age_retraite - age_actuel
    simulation_results = []

    if mode_versements == 'FIX':
        # Simulation pour des versements fixes
        montant_annuel = float(request.form.get('VERS_ANN', 0))

        for annee in range(annees_jusqu_retraite):
            simulation_results.append({
                'annee': age_actuel + annee,
                'montant_verse': montant_annuel
            })
    elif mode_versements == 'PROP':
        # Simulation pour des versements proportionnels au salaire
        pourcentage_salaire = float(request.form.get('PERC_SAL', 0))
        revenus_annuels_2023 = float(request.form.get('REV_0', 0))
        taux_augmentation_salaire = float(request.form.get('TX_AUG_SAL', 0)) / 100

        revenus_annuels = revenus_annuels_2023
        for annee in range(annees_jusqu_retraite):
            montant_verse = (pourcentage_salaire / 100) * revenus_annuels
            simulation_results.append({
                'annee': age_actuel + annee,
                'montant_verse': montant_verse
            })
            revenus_annuels *= (1 + taux_augmentation_salaire)

    return render_template('simulation_resultats.html', simulation_results=simulation_results)


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
    db.create_all() 
    app.run(debug=True)
