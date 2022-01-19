from django import forms
from events.models import Event, Enroll
from utils.forms import update_fields_widget


class EventEnrollForm(forms.ModelForm):
    class Meta:
        model = Enroll
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()

        if Enroll.objects.filter(user=cleaned_data['user'], event=cleaned_data['event']).exists():
            raise forms.ValidationError(f'Вы уже записаны на это событие!')

        return cleaned_data


class EventCreateUpdateForm(forms.ModelForm):
    date_start = forms.DateTimeField(label='Дата начала',
                                     widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M",
                                                                attrs={'type': 'datetime-local'})
                                     )

    class Meta:
        model = Event
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('title', 'description', 'date_start', 'logo',), 'form-control')
        self.fields['is_private'].widget.attrs.update({'class': 'form-check-label'})
        update_fields_widget(self, ('participants_number', 'category', 'features',), 'form-select')

    def clean(self):
        cleaned_data = super().clean()
        participants_number = cleaned_data.get('participants_number')
        if participants_number and participants_number < 5:
            raise forms.ValidationError('Количество участников должно быть от 5')
        return cleaned_data
