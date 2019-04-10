from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed

from convert_functions import PICTURE_SUPPORTED_FORMATS, AUDIO_SUPPORTED_FORMATS, VIDEO_SUPPORTED_FORMATS


class PictureForm(FlaskForm):
    field = FileField('Choose file', validators=[FileRequired(),
                                                 FileAllowed([x.lower() for x in PICTURE_SUPPORTED_FORMATS],
                                                             'Unsupported type')])
    format = SelectField('Format', choices=[(x, x.lower()) for x in PICTURE_SUPPORTED_FORMATS],
                         validators=[])
    submit = SubmitField('Convert!')


class AudioForm(FlaskForm):
    field = FileField('Choose file', validators=[FileRequired(),
                                                 FileAllowed([x.lower() for x in AUDIO_SUPPORTED_FORMATS],
                                                             'Unsupported type')])
    format = SelectField('Format', choices=[(x, x.lower()) for x in AUDIO_SUPPORTED_FORMATS],
                         validators=[])
    submit = SubmitField('Convert!')


class VideoForm(FlaskForm):
    field = FileField('Choose file', validators=[FileRequired(),
                                                 FileAllowed([x.lower() for x in VIDEO_SUPPORTED_FORMATS],
                                                             'Only Archives')])
    format = SelectField('Format', choices=[(x, x.lower()) for x in VIDEO_SUPPORTED_FORMATS],
                         validators=[])  # TODO: validation
    submit = SubmitField('Convert!')
