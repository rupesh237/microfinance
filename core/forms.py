from django import forms
from django.forms import modelformset_factory
from .models import CollectionSheet

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
