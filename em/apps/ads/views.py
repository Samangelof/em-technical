# em/apps/ads/views.py  
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from core.models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(f"Created user: {user}")
            login(request, user)
            return redirect('ad_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('ad_list')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('ad_list')



# ------------------------------------------------
def ad_list(request):
    ads = Ad.objects.all()
    return render(request, 'ads/ad_list.html', {'ads': ads})

def ad_detail(request, ad_id):
    try:
        ad = Ad.objects.get(id=ad_id)
    except Ad.DoesNotExist:
        return HttpResponseNotFound('Объявление не найдено')
    return render(request, 'ads/ad_detail.html', {'ad': ad})


@login_required
def create_ad(request):
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return redirect('ad_list')
    else:
        form = AdForm()
    return render(request, 'ads/ad_form.html', {'form': form})


@login_required
def edit_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)

    if request.user != ad.user:
        return HttpResponseForbidden("У вас нет прав на редактирование этого объявления")

    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('ad_detail', ad_id=ad.id)
    else:
        form = AdForm(instance=ad)
    return render(request, 'ads/ad_form.html', {'form': form, 'ad': ad})


@require_http_methods(["GET", "POST"])
@login_required(login_url='/login/')
def delete_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)

    if request.user != ad.user:
        return HttpResponseForbidden("У вас нет прав на удаление этого объявления")

    if request.method == 'POST':
        ad.delete()
        return redirect('ad_list')
    return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})


@login_required
def create_exchange_proposal(request, ad_id):
    ad_sender = get_object_or_404(Ad, id=ad_id)
    if ad_sender.user == request.user:
        return HttpResponseForbidden("Нельзя предложить обмен самому себе")

    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST)
        if form.is_valid():
            ad_receiver = form.cleaned_data['ad_receiver']
            if ExchangeProposal.objects.filter(ad_sender=ad_sender, ad_receiver=ad_receiver, status='pending').exists():
                return HttpResponseForbidden("Предложение обмена уже существует")

            proposal = form.save(commit=False)
            proposal.ad_sender = ad_sender
            proposal.status = 'pending'
            proposal.save()
            return redirect('ad_list')
    else:
        form = ExchangeProposalForm()
    return render(request, 'ads/create_exchange_proposal.html', {'form': form, 'ad': ad_sender})


@login_required
def update_exchange_proposal_status(request, proposal_id, new_status):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)

    if proposal.ad_receiver.user != request.user:
        return HttpResponseForbidden("Вы не можете изменить статус этого предложения.")

    proposal.status = new_status
    proposal.save()
    return redirect('ad_list')


@login_required
def my_exchanges(request):
    sent_proposals = ExchangeProposal.objects.filter(
        ad_sender__user=request.user
    ).select_related('ad_sender', 'ad_receiver')
    
    received_proposals = ExchangeProposal.objects.filter(
        ad_receiver__user=request.user
    ).select_related('ad_sender', 'ad_receiver')
    
    return render(request, 'ads/my_exchanges.html', {
        'sent_proposals': sent_proposals,
        'received_proposals': received_proposals
    })


def custom_404_view(request, exception):
    return render(request, 'ads/404_not_found.html', status=404)