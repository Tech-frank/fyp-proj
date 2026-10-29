from django import forms


class SignupForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    password_field_name = "password_confirm"

    def clean(self):
        data = super().clean()
        if data.get("password") != data.get(self.password_field_name):
            raise forms.ValidationError("Passwords do not match.")
        return data
