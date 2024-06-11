from django import forms

class YouTubeURLForm(forms.Form):
    '''Form to accept youtube URL from user'''
    url = forms.URLField(label='Youtube URL', max_length=400)


class QualitySelectionForm(forms.Form):
    '''Form to accept quality selection from user'''
    quality = forms.ChoiceField(label='Quality', choices=[])
