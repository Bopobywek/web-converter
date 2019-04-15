from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, SelectField

from archive_functions import SUPPORTED_ARCHIVE_FORMATS_FOR_FORMS
from convert_functions import PICTURE_SUPPORTED_FORMATS, AUDIO_SUPPORTED_FORMATS, VIDEO_SUPPORTED_FORMATS


class PictureForm(FlaskForm):
    file = FileField('Choose file', validators=[FileRequired(),
                                                FileAllowed([x.lower() for x in PICTURE_SUPPORTED_FORMATS],
                                                            'Unsupported type')])
    file_format = SelectField('Format', choices=[(x, x.lower()) for x in PICTURE_SUPPORTED_FORMATS])
    submit = SubmitField('Convert!')


class AudioForm(FlaskForm):
    file = FileField('Choose file', validators=[FileRequired(),
                                                FileAllowed([x.lower() for x in AUDIO_SUPPORTED_FORMATS],
                                                            'Unsupported type')])
    file_format = SelectField('Format', choices=[(x, x.lower()) for x in AUDIO_SUPPORTED_FORMATS])
    submit = SubmitField('Convert!')


class VideoForm(FlaskForm):
    file = FileField('Choose file', validators=[FileRequired(),
                                                FileAllowed([x.lower() for x in VIDEO_SUPPORTED_FORMATS],
                                                            'Unsupported type')])
    file_format = SelectField('Format', choices=[(x, x.lower()) for x in VIDEO_SUPPORTED_FORMATS])
    submit = SubmitField('Convert!')


class ArchiveOpenForm(FlaskForm):
    file = FileField('Choose file', validators=[FileRequired(),
                                                FileAllowed(SUPPORTED_ARCHIVE_FORMATS_FOR_FORMS.values(),
                                                            'Unsupported type')])
    submit = SubmitField('Open!')


class ArchiveConvertForm(FlaskForm):
    file = FileField('Choose file', validators=[FileRequired(),
                                                FileAllowed(SUPPORTED_ARCHIVE_FORMATS_FOR_FORMS.values(),
                                                            'Unsupported type')])
    submit = SubmitField('Open!')


class ArchiveConvertForm2(FlaskForm):
    submit2 = SubmitField('Convert!')
