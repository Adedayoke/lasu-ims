from django import forms
from core.models import Asset, AssetCategory, Department
from accounts.models import User


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'name', 'description', 'category', 'department', 'custodian',
            'status', 'condition', 'purchase_date', 'purchase_cost',
            'supplier_name', 'serial_number', 'location_description', 'notes',
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'location_description': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.Textarea, forms.DateInput, forms.Select, forms.CheckboxInput)):
                field.widget.attrs.setdefault('class', 'form-control')
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')

        self.fields['custodian'].queryset = User.objects.filter(is_active=True).order_by('first_name')
        self.fields['custodian'].required = False


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'}),
    )

    def clean_csv_file(self):
        f = self.cleaned_data['csv_file']
        if not f.name.lower().endswith('.csv'):
            raise forms.ValidationError('Only CSV files are accepted.')
        if f.content_type not in ('text/csv', 'application/csv', 'text/plain', 'application/vnd.ms-excel'):
            raise forms.ValidationError('File must be a valid CSV.')
        return f
