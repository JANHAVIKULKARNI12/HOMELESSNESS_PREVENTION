# Donor Model
class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    donation_house = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    donation_description = db.Column(db.Text, nullable=True)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Donor {self.name}>"

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Donor Page Route
@app.route('/donor', methods=['GET', 'POST'])
def donor():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        donation_house = request.form['donation_house']
        address = request.form['address']
        donation_description = request.form['donation_description']

        # Create a new Donor instance
        new_donor = Donor(
            name=name,
            email=email,
            phone_number=phone_number,
            donation_house=donation_house,
            address=address,
            donation_description=donation_description
        )

        # Add and commit the new donor to the database
        db.session.add(new_donor)
        db.session.commit()
        
        flash('Thank you for your donation!', 'success')
        return redirect(url_for('donor'))

    # Retrieve all donors to display
    donors = Donor.query.all()
    return render_template('donor_form.html', donors=donors)