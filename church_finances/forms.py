from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Transaction, Member, Tithing


class CustomUserCreationForm(UserCreationForm):
    """
    A custom user creation form to extend Django's default.
    You can add more fields here if needed in the future.
    """

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + (
            "email",
        )  # Add email field to registration


class TransactionForm(forms.ModelForm):
    """
    Form for creating and updating financial transactions.
    """

    # Override category field to dynamically show choices based on type if needed
    # For simplicity, we combine all categories here.
    # In a more complex app, you might use JavaScript to filter categories based on type selection.

    class Meta:
        model = Transaction
        fields = ["date", "type", "category", "amount", "description"]
        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date", "class": "form-input rounded-md shadow-sm"}
            ),
            "type": forms.Select(attrs={"class": "form-select rounded-md shadow-sm"}),
            "category": forms.Select(
                attrs={"class": "form-select rounded-md shadow-sm"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-input rounded-md shadow-sm", "step": "0.01"}
            ),
            "description": forms.Textarea(
                attrs={"rows": 3, "class": "form-textarea rounded-md shadow-sm"}
            ),
        }
        labels = {
            "date": "Date",
            "type": "Transaction Type",
            "category": "Category",
            "amount": "Amount ($)",
            "description": "Description (Optional)",
        }


class MemberForm(forms.ModelForm):
    """
    Form for creating and updating church members.
    """

    class Meta:
        model = Member
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "member_since",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-input rounded-md shadow-sm"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-input rounded-md shadow-sm"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-input rounded-md shadow-sm"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-input rounded-md shadow-sm"}
            ),
            "address": forms.Textarea(
                attrs={"rows": 3, "class": "form-textarea rounded-md shadow-sm"}
            ),
            "member_since": forms.DateInput(
                attrs={"type": "date", "class": "form-input rounded-md shadow-sm"}
            ),
        }
        labels = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email Address",
            "phone": "Phone Number",
            "address": "Address",
            "member_since": "Member Since",
        }


class TithingForm(forms.ModelForm):
    """
    Form for recording individual tithing.
    """

    class Meta:
        model = Tithing
        fields = [
            "member",
            "date",
            "amount",
            "payment_method",
            "check_number",
            "notes",
        ]
        widgets = {
            "member": forms.Select(
                attrs={"class": "form-select rounded-md shadow-sm"}
            ),
            "date": forms.DateInput(
                attrs={"type": "date", "class": "form-input rounded-md shadow-sm"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-input rounded-md shadow-sm", "step": "0.01"}
            ),
            "payment_method": forms.Select(
                attrs={"class": "form-select rounded-md shadow-sm"}
            ),
            "check_number": forms.TextInput(
                attrs={"class": "form-input rounded-md shadow-sm"}
            ),
            "notes": forms.Textarea(
                attrs={"rows": 3, "class": "form-textarea rounded-md shadow-sm"}
            ),
        }
        labels = {
            "member": "Member",
            "date": "Date",
            "amount": "Amount ($)",
            "payment_method": "Payment Method",
            "check_number": "Check Number",
            "notes": "Notes (Optional)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active members
        self.fields["member"].queryset = Member.objects.filter(is_active=True)


class TithingFilterForm(forms.Form):
    """
    Form for filtering tithing records.
    """

    member = forms.ModelChoiceField(
        queryset=Member.objects.filter(is_active=True),
        required=False,
        empty_label="All Members",
        widget=forms.Select(attrs={"class": "form-select rounded-md shadow-sm"}),
    )
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-input rounded-md shadow-sm",
                "placeholder": "Year (e.g., 2024)",
            }
        ),
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-input rounded-md shadow-sm"}
        ),
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-input rounded-md shadow-sm"}
        ),
    )
