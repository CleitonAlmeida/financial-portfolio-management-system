from django import forms
from portfolio.selectors import get_portfolios

class AssetUploadFileForm(forms.Form):
    myfile = forms.FileField()

class TransactionUploadFileForm(forms.Form):
    _choices = []

    def __init__(self, user, *args, **kwargs):
        self._choices = []
        portfolios = get_portfolios(fetched_by=user)
        for p in portfolios:
            self._choices.append((p.pk, p.name))
        super(TransactionUploadFileForm, self).__init__(*args, **kwargs)
        self.fields['portfolio'] = forms.ChoiceField(choices=self._choices)

    portfolio = forms.ChoiceField(widget=forms.Select(choices=[]))
    myfile = forms.FileField()
