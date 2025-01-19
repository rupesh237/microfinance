from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VaultTransaction, TellerToTellerTransaction, DailyCashSummary


@receiver(post_save, sender=VaultTransaction)
def update_daily_cash_summary_for_vault(sender, instance, **kwargs):
    if instance.status != "Approved":
        return

    branch = instance.cash_vault.branch
    date = instance.date.date()

    daily_summary, _ = DailyCashSummary.objects.get_or_create(
        branch=branch,
        date=date,
        defaults={'opening_vault_balance': instance.cash_vault.current_balance},
    )

    # Update vault balance
    # Update teller balances for teller-related transactions
    teller_balances = daily_summary.teller_balances or {}
    teller_name = instance.teller.employee.employee_detail.name
    current_balance = float(teller_balances.get(teller_name, 0))
    closing_balance = daily_summary.closing_vault_balance or daily_summary.opening_vault_balance
    if instance.transaction_type == "Deposit":
        daily_summary.closing_vault_balance = closing_balance + instance.amount
        teller_balances[teller_name] = current_balance - float(instance.amount)
    elif instance.transaction_type == "Withdraw":
        daily_summary.closing_vault_balance = closing_balance - instance.amount
        teller_balances[teller_name] = current_balance + float(instance.amount)

    daily_summary.teller_balances = teller_balances

    daily_summary.save()


@receiver(post_save, sender=TellerToTellerTransaction)
def update_daily_cash_summary_for_teller_transaction(sender, instance, **kwargs):
    if instance.status != "Approved":
        return

    branch = instance.branch
    date = instance.date.date()

    daily_summary, _ = DailyCashSummary.objects.get_or_create(
        branch=branch,
        date=date,
        defaults={'opening_vault_balance': 0},  # Default value if vault balance is not initialized
    )

    # Update teller balances
    teller_balances = daily_summary.teller_balances or {}

    # From Teller
    from_teller_name = instance.from_teller.employee.employee_detail.name
    from_current_balance = float(teller_balances.get(from_teller_name, 0))
    teller_balances[from_teller_name] = from_current_balance - float(instance.amount)

    # To Teller
    to_teller_name = instance.to_teller.employee.employee_detail.name
    to_current_balance = float(teller_balances.get(to_teller_name, 0))
    teller_balances[to_teller_name] = to_current_balance + float(instance.amount)

    daily_summary.teller_balances = teller_balances
    daily_summary.save()

