from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VaultTransaction, TellerToTellerTransaction, DailyCashSummary

from decimal import Decimal


@receiver(post_save, sender=VaultTransaction)
def update_daily_cash_summary_for_vault(sender, instance, **kwargs):
    if instance.status != "Approved":
        return

    branch = instance.cash_vault.branch
    date = instance.date.date()

    daily_summary, _ = DailyCashSummary.objects.get_or_create(
        branch=branch,
        date=date,
        defaults={'opening_vault_balance': instance.cash_vault.balance},
    )

    # Update vault balance
    # Update teller balances for teller-related transactions
    teller_balances = daily_summary.teller_balances or {}
    teller_name = instance.teller.employee.employee_detail.name
     # Get the current balance for the teller
    current_balance = teller_balances.get(teller_name, {}).get('closing_balance', 0)
    teller_opening_balance = instance.teller.balance

    # Get the opening vault balance
    opening_vault_balance = daily_summary.opening_vault_balance
    closing_vault_balance = daily_summary.closing_vault_balance or opening_vault_balance

    # Handle transaction types (Deposit or Withdraw)
    if instance.transaction_type == "Deposit":
        # Update vault balance
        daily_summary.closing_vault_balance = closing_vault_balance + Decimal(instance.amount)
        
        # Update teller balance (credit)
        teller_balances[teller_name] = {
            'debit': float(teller_balances.get(teller_name, {}).get('debit', 0)) + float(instance.amount),
            'credit': float(teller_balances.get(teller_name, {}).get('credit', 0)),
            'opening_balance': float(teller_opening_balance),
            'closing_balance': float(current_balance) - float(instance.amount),
        }

    elif instance.transaction_type == "Withdraw":
        # Update vault balance
        daily_summary.closing_vault_balance = closing_vault_balance - Decimal(instance.amount)
        
        teller_balances[teller_name] = {
            'debit': float(teller_balances.get(teller_name, {}).get('debit', 0)),
            'credit': float(teller_balances.get(teller_name, {}).get('credit', 0)) + float(instance.amount),
            'opening_balance': float(current_balance),
            'closing_balance': float(current_balance) + float(instance.amount),
        }

    # Save the updated teller balances and daily summary
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
    from_current_balance = teller_balances.get(from_teller_name, {}).get('closing_balance', 0)
    from_opening_balance = instance.from_teller.balance  # Get balance from instance

    # To Teller
    to_teller_name = instance.to_teller.employee.employee_detail.name
    to_current_balance = teller_balances.get(to_teller_name, {}).get('closing_balance', 0)
    to_opening_balance = instance.to_teller.balance

    # Handle the transaction from the 'From Teller'
    teller_balances[from_teller_name] = {
        'debit': float(teller_balances.get(from_teller_name, {}).get('debit', 0)) + float(instance.amount),
        'credit': float(teller_balances.get(from_teller_name, {}).get('credit', 0)),
        'opening_balance': float(from_opening_balance),
        'closing_balance': float(from_opening_balance) - float(instance.amount),
        'transaction_type': 'Transfer Out',
        'transaction_target': f'From Teller: {from_teller_name}'
    }

    # Handle the transaction to the 'To Teller'
    teller_balances[to_teller_name] = {
        'debit': float(teller_balances.get(to_teller_name, {}).get('debit', 0)),
        'credit': float(teller_balances.get(to_teller_name, {}).get('credit', 0)) + float(instance.amount),
        'opening_balance': float(to_opening_balance),
        'closing_balance': float(to_opening_balance) + float(instance.amount),
        'transaction_type': 'Transfer In',
        'transaction_target': f'To Teller: {to_teller_name}'
    }

    # Save the updated teller balances and daily summary
    daily_summary.teller_balances = teller_balances
    daily_summary.save()

