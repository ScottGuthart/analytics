from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, DataRequired, FileAllowed
from wtforms import SubmitField

class FileForm(FlaskForm):
    max_diff_data = FileField('Max Diff Data', validators=[FileRequired(), FileAllowed(['xlsx'])])
    ranking_data = FileField('Ranking Data', validators=[FileRequired(), FileAllowed(['xlsx'])])
    design = FileField('Max Diff Design', validators=[FileRequired(), FileAllowed(['xlsx'])])
    win_loss_rates = FileField('Win / Loss Rates', validators=[FileRequired(), FileAllowed(['xlsx'])])
    submit = SubmitField('Upload', validators=[])