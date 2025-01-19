from django.test import TestCase
from django.utils.timezone import now
from core.models import (
    Branch, CashVault, Teller, BankAccount, CashTransaction, DailyCashSummary
)

class DailyCashSummarySignalTests(TestCase):

    def setUp(self):
        # Set up branch and related models
        self.branch = Branch.objects.create(name="Test Branch")
        self.cash_vault = CashVault.objects.create(branch=self.branch, current_balance=10000)
        self.teller = Teller.objects.create(branch=self.branch, name="Teller 1", current_balance=5000)
        self.bank_account = BankAccount.objects.create(branch=self.branch, current_balance=20000)

    def test_deposit_to_vault_updates_daily_cash_summary(self):
        # Create a transaction for depositing cash to vault
        transaction = CashTransaction.objects.create(
            cash_vault=self.cash_vault,
            transaction_type=CashTransaction.TransactionType.DEPOSIT_TO_VAULT,
            amount=2000,
            date=now()
        )

        # Verify the daily cash summary is updated
        daily_summary = DailyCashSummary.objects.get(branch=self.branch, date=now().date())
        self.assertEqual(daily_summary.closing_vault_balance, 12000)  # 10000 + 2000

    def test_withdraw_from_vault_updates_daily_cash_summary(self):
        # Create a transaction for withdrawing cash from the vault
        transaction = CashTransaction.objects.create(
            cash_vault=self.cash_vault,
            transaction_type=CashTransaction.TransactionType.WITHDRAW_FROM_VAULT,
            amount=3000,
            date=now()
        )

        # Verify the daily cash summary is updated
        daily_summary = DailyCashSummary.objects.get(branch=self.branch, date=now().date())
        self.assertEqual(daily_summary.closing_vault_balance, 7000)  # 10000 - 3000

    def test_transfer_to_bank_updates_daily_cash_summary(self):
        # Create a transaction for transferring cash to the bank
        transaction = CashTransaction.objects.create(
            cash_vault=self.cash_vault,
            transaction_type=CashTransaction.TransactionType.TRANSFER_TO_BANK,
            amount=5000,
            date=now()
        )

        # Verify the daily cash summary is updated
        daily_summary = DailyCashSummary.objects.get(branch=self.branch, date=now().date())
        self.assertEqual(daily_summary.closing_vault_balance, 5000)  # 10000 - 5000
        self.assertEqual(daily_summary.closing_bank_balance, 25000)  # 20000 + 5000

    def test_transfer_from_bank_updates_daily_cash_summary(self):
        # Create a transaction for transferring cash from the bank
        transaction = CashTransaction.objects.create(
            cash_vault=self.cash_vault,
            transaction_type=CashTransaction.TransactionType.TRANSFER_FROM_BANK,
            amount=4000,
            date=now()
        )

        # Verify the daily cash summary is updated
        daily_summary = DailyCashSummary.objects.get(branch=self.branch, date=now().date())
        self.assertEqual(daily_summary.closing_vault_balance, 14000)  # 10000 + 4000
        self.assertEqual(daily_summary.closing_bank_balance, 16000)  # 20000 - 4000

    def test_teller_disbursement_updates_daily_cash_summary(self):
        # Create a transaction for disbursing cash to a teller
        transaction = CashTransaction.objects.create(
            teller=self.teller,
            transaction_type=CashTransaction.TransactionType.TELLER_DISBURSEMENT,
            amount=2000,
            date=now()
        )

        # Verify the daily cash summary is updated
        daily_summary = DailyCashSummary.objects.get(branch=self.branch, date=now().date())
        self.assertEqual(daily_summary.teller_balances[self.teller.name], 7000)  # 5000 + 2000

    def test_teller_receipt_updates_daily_cash_summary(self):
        # Create a transaction for receiving cash from a teller
        transaction = CashTransaction.objects.create(
            teller=self.teller,
            transaction_type=CashTransaction.TransactionType.TELLER_RECEIPT,
            amount=1000,
            date=now()
        )

        # Verify the daily cash summary is updated
        daily_summary = DailyCashSummary.objects.get(branch=self.branch, date=now().date())
        self.assertEqual(daily_summary.teller_balances[self.teller.name], 4000)  # 5000 - 1000
