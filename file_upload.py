from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, SelectField

from archive_functions import ARCHIVE_SUPPORTED_FORMATS, SUPPORTED_SUFFIXES
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


class VideoForm(FlaskForm):  # TODO: change name of first and second attributes
    field = FileField('Choose file', validators=[FileRequired(),
                                                 FileAllowed([x.lower() for x in VIDEO_SUPPORTED_FORMATS],
                                                             'Unsupported type')])
    format = SelectField('Format', choices=[(x, x.lower()) for x in VIDEO_SUPPORTED_FORMATS],
                         validators=[])  # TODO: validation
    submit = SubmitField('Convert!')


class ArchiveOpenForm(FlaskForm):
    file = FileField('Choose file', validators=[FileRequired(), FileAllowed(ARCHIVE_SUPPORTED_FORMATS,
                                                                            'Unsupported type')])
    submit = SubmitField('Open')
