from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from portfolio.models import Transaction, Portfolio

@receiver(post_save, sender=Transaction)
def set_unconsolidated(sender, **kwargs):
    transaction = kwargs['instance']
    portfolio = Portfolio.objects.filter(pk=transaction.portfolio.pk)
    portfolio.update(consolidated = False)

    Transaction.objects.filter(pk=transaction.pk).update(consolidated = False)
    print("Request Transaction finished!")

@receiver(post_delete, sender=Transaction)
def set_unconsolidated(sender, **kwargs):
    transaction = kwargs['instance']
    portfolio = Portfolio.objects.filter(pk=transaction.portfolio.pk)
    portfolio.update(consolidated = False)

    t = Transaction.objects.filter(
            portfolio__pk=transaction.portfolio.pk,
            asset__pk=transaction.asset.pk
        ).update(consolidated = False)
    print('transaction %s', t)
    print("Delete Transaction finished!")
