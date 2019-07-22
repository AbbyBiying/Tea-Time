from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, DateTimeField,
                     RadioField,SelectField,TextField,
                     TextAreaField,SubmitField)
# create a WTForm Class 
class InfoForm(FlaskForm):    
    # drink_tea  = BooleanField("Do you drink tea?")
    temperature = RadioField('Hot tea/iced tea:', choices=[('hot','Hot Tea'),('iced','Iced Tea')])
    tea_choice = SelectField(u'Pick Your Favorite Tea:',
                          choices=[('Black', 'Black tea'), ('Green', 'Green tea'),
                                   ('Oolong', 'Oolong tea'),('Pu-erh','Pu-erh tea'),
                                   ('Masala_chai', 'Masala chai')])
    submit = SubmitField('Submit')

class AddTeaForm(FlaskForm):    
    temperature = RadioField('Hot tea/iced tea:', choices=[('hot','Hot Tea'),('iced','Iced Tea')])
    tea_choice = StringField("Type of Tea: ")

    submit = SubmitField('Add Tea')

