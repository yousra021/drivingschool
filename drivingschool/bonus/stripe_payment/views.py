import stripe
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.conf import settings
from planning.models import LessonPackage, LessonPurchase
from .forms import LessonPurchaseForm

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def purchase_lesson(request):
    if request.user.role != 'STUDENT':
        return HttpResponseForbidden("Accès réservé aux élèves.")

    if request.method == 'POST':
        form = LessonPurchaseForm(request.POST)
        if form.is_valid():
            hours = int(form.cleaned_data['hours'])
            amount = hours * 65

            purchase = LessonPurchase.objects.create(
                student=request.user,
                hours_purchased=hours,
                amount_paid=amount,
                payment_status='PENDING'
            )

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': f'{hours} heure(s) de conduite',
                        },
                        'unit_amount': int(amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/bonus/purchase/success/') + f"?purchase_id={purchase.id}",
                cancel_url=request.build_absolute_uri('/bonus/purchase/cancel/'),
            )
            return redirect(checkout_session.url, code=303)
    else:
        form = LessonPurchaseForm()

    return render(request, 'stripe_payment/purchase_lesson.html', {'form': form})


@login_required
def purchase_success(request):
    purchase_id = request.GET.get("purchase_id")
    if purchase_id:
        try:
            purchase = LessonPurchase.objects.get(id=purchase_id, student=request.user)
            purchase.payment_status = 'PAID'
            purchase.save()

            package, _ = LessonPackage.objects.get_or_create(student=request.user)
            package.total_hours += purchase.hours_purchased 
            package.save()
        except LessonPurchase.DoesNotExist:
            pass

    return render(request, 'stripe_payment/success.html')


@login_required
def purchase_cancel(request):
    return render(request, 'stripe_payment/cancel.html')
