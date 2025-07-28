from django.db import models
from django.contrib.auth.models import User  # Import Django's built-in User model


class Member(models.Model):
    """
    Model to represent a church member for tithing tracking.
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    member_since = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def total_tithes(self, year=None):
        """Calculate total tithes for this member, optionally for a specific year."""
        tithes = self.tithes.filter(is_active=True)
        if year:
            tithes = tithes.filter(date__year=year)
        return sum(tithe.amount for tithe in tithes)


class Tithing(models.Model):
    """
    Model to represent individual tithing records.
    """

    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="tithes"
    )
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("cash", "Cash"),
            ("check", "Check"),
            ("bank_transfer", "Bank Transfer"),
            ("card", "Credit/Debit Card"),
            ("other", "Other"),
        ],
        default="cash",
    )
    check_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)  # For soft deletes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.member.full_name} - {self.date} - ${self.amount}"


class Transaction(models.Model):
    """
    Model to represent a financial transaction (income or expense).
    """

    TRANSACTION_TYPES = (
        ("income", "Income"),
        ("expense", "Expense"),
    )

    # Common categories for church finances
    INCOME_CATEGORIES = (
        ("tithes", "Tithes"),
        ("offerings", "Offerings"),
        ("donations", "Donations"),
        ("fundraising", "Fundraising"),
        ("other_income", "Other Income"),
    )

    EXPENSE_CATEGORIES = (
        ("salaries", "Salaries"),
        ("utilities", "Utilities"),
        ("rent_mortgage", "Rent/Mortgage"),
        ("missions", "Missions"),
        ("benevolence", "Benevolence"),
        ("supplies", "Supplies"),
        ("maintenance", "Maintenance"),
        ("events", "Events"),
        ("other_expense", "Other Expense"),
    )

    date = models.DateField()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(
        max_length=50,
        choices=INCOME_CATEGORIES + EXPENSE_CATEGORIES,
        help_text="Select a category for the transaction.",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "-date",
            "-created_at",
        ]  # Order by date descending, then creation time

    def __str__(self):
        return (
            f"{self.date} - {self.get_type_display()}: {self.category} - ${self.amount}"
        )
