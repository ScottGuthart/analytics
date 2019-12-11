from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, IntegerField
from wtforms.validators import ValidationError,  InputRequired

class PairsForm(FlaskForm):
    max_diff_data = FileField('Max Diff Data', validators=[FileRequired(), FileAllowed(['xlsx'])])
    ranking_data = FileField('Ranking Data', validators=[FileRequired(), FileAllowed(['xlsx'])])
    design = FileField('Max Diff Design', validators=[FileRequired(), FileAllowed(['xlsx'])])
    win_loss_rates = FileField('Win / Loss Rates', validators=[FileRequired(), FileAllowed(['xlsx'])])
    submit = SubmitField('Upload', validators=[])

class DesignForm(FlaskForm):
    design = FileField('Sawtooth Design CSV', validators=[FileRequired(), FileAllowed(['csv'])])
    num_to_keep = IntegerField('Desired Number of Items', validators=[InputRequired()])
    submit = SubmitField('Upload', validators=[])

    def validate_num_to_keep(self, num_to_keep):
        if num_to_keep.data < 10:
            raise ValidationError("Please enter the number of items you'd like in the final design here")