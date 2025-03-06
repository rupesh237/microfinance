from django import forms
from django.forms import modelformset_factory
from .models import CollectionSheet, Voucher, VoucherEntry

# class VoucherEntryForm(forms.ModelForm):
#     class Meta:
#         model = VoucherEntry
#         fields = ['account', 'amount', 'entry_type', 'memo']

class VoucherForm(forms.ModelForm):
      class Meta:
        model = Voucher
        fields = ['in_word', 'narration', 'cheque_no', 'encloser']
        widgets = {
            'in_word': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Amount in words'}),
            'narration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Narration', 'required': True}),
            'cheque_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cheque number'}),
            'encloser': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter encloser'}),
        }

# Create a custom form for the CollectionSheet model
class CollectionSheetForm(forms.ModelForm):
    class Meta:
        model = CollectionSheet
        fields = ['member_collection', 'special_record',]


    # def __init__(self, *args, **kwargs):
    #     super(CollectionSheetForm, self).__init__(*args, **kwargs)
    #     self.fields['evaluation_no'].required = False
    #     self.fields['meeting_by'].required = False
    #     self.fields['supervision_by_1'].required = False
    #     self.fields['supervision_by_2'].required = False
    #     self.fields['next_meeting_date'].required = False
    #     self.fields['total'].required = False
