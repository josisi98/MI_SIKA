from flask import Flask, request, flash, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_migrate import Migrate
import os
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.secret_key = 'lavienestrien'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MI_SIKA.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    messages = db.relationship('Message', backref='expediteur', lazy=True)

    def __repr__(self):
        return f'Utilisateur({self.nom}, {self.email})'
    
class EtapeForm(FlaskForm):
    statut_professionnel = StringField('Statut professionnel', validators=[DataRequired()])
    revenus_annuels_2023 = FloatField('Revenus annuels 2023', validators=[DataRequired()])
    progression_annuelle = IntegerField('Progression annuelle', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    mode_versements = StringField('Mode de versements', validators=[DataRequired()])
    versements_annee = FloatField('Versements par année', validators=[DataRequired()])
    versements_proportionnels = FloatField('Versements proportionnels', validators=[DataRequired()])
    age_retraite = IntegerField('Âge de la retraite', validators=[DataRequired()])
    versements_fixes = FloatField('Versements fixes', validators=[DataRequired()])
    progression_annuelle_revenus = IntegerField('Progression annuelle des revenus', validators=[DataRequired()])

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sujet = db.Column(db.String(200), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    expediteur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)

def send_email(name, email, subject, message):
    sender_email = 'votre_adresse@gmail.com'
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'votre_adresse@gmail.com'
    smtp_password = 'votre_mot_de_passe'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    body = f"Nom : {name}\nEmail : {email}\nMessage :\n{message}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, email, msg.as_string())
            return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {str(e)}")
        return False

@app.route('/')
def accueil():
    return render_template('Accueil.html', title='Accueil')

@app.route('/apropos')
def apropos():
    return render_template('Apropos.html', title='À propos')

@app.route('/simulateur', methods=['GET', 'POST'])
def simulateur():
    if request.method == 'POST':
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
        return redirect(url_for('etape_suivante'))
    return render_template('resultat.html')

@app.route('/simulation', methods=['POST'])
def simulation():
    age_actuel = int(request.form.get('AGE_0', 0))
    age_retraite = int(request.form.get('AGE_END', 0))
    mode_versements = request.form.get('MOD_VERS')

    annees_jusqu_retraite = age_retraite - age_actuel
    simulation_results = []

    if mode_versements == 'FIX':
        montant_annuel = float(request.form.get('VERS_ANN', 0))

        for annee in range(annees_jusqu_retraite):
            simulation_results.append({
                'annee': age_actuel + annee,
                'montant_verse': montant_annuel
            })
    elif mode_versements == 'PROP':
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
        flash('Votre message a été envoyé avec succès!', 'success')
    else:
        flash("Erreur lors de l'envoi de l'e-mail.", 'danger')

    return redirect(url_for('accueil'))

def recreate_db():
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    if os.path.exists('MI_SIKA.db'):
        os.remove('MI_SIKA.db')
        recreate_db()
    app.run(debug=True)
